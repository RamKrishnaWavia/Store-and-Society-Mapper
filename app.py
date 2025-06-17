import streamlit as st
import pandas as pd
import numpy as np
import io
from scipy.spatial import cKDTree
from math import radians, cos, sin, asin, sqrt

# Haversine formula
EARTH_RADIUS_KM = 6371.0

def haversine_np(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))

st.title("Society to Nearest Dark Store Mapper")

# Downloadable sample CSV templates
sample_societies = pd.DataFrame({
    'City': ['Ahmedabad-Gandhinagar'],
    'Society_name': ['Aditya Parivesh'],
    'latitude': [23.038891],
    'longitude': [72.618126]
})

sample_darkstores = pd.DataFrame({
    'Store name as per projects': ['South Bopal'],
    'Latitude': [23.018329],
    'Longitude': [72.469856]
})

st.download_button(
    label="Download Societies Template (CSV)",
    data=sample_societies.to_csv(index=False).encode(),
    file_name="societies_template.csv",
    mime="text/csv"
)

st.download_button(
    label="Download Dark Stores Template (CSV)",
    data=sample_darkstores.to_csv(index=False).encode(),
    file_name="darkstores_template.csv",
    mime="text/csv"
)

societies_file = st.file_uploader("Upload Societies CSV", type=["csv"])
darkstores_file = st.file_uploader("Upload Dark Stores CSV", type=["csv"])

if societies_file and darkstores_file:
    with st.spinner("Processing... Please wait."):
        societies_df = pd.read_csv(societies_file)
        darkstores_df = pd.read_csv(darkstores_file)

        # Convert lat/lon to radians for efficient vectorized distance
        darkstore_coords = np.radians(darkstores_df[['Latitude', 'Longitude']].values)
        society_coords = np.radians(societies_df[['latitude', 'longitude']].values)

        # Build KDTree and query
        tree = cKDTree(darkstore_coords)
        dist_rad, idx = tree.query(society_coords, k=1)

        # Compute haversine distance in km
        dists_km = haversine_np(societies_df['latitude'].values, societies_df['longitude'].values,
                                darkstores_df.iloc[idx]['Latitude'].values,
                                darkstores_df.iloc[idx]['Longitude'].values)

        # Build result DataFrame
        result_df = pd.DataFrame({
            'City': societies_df['City'],
            'Society Name': societies_df['Society_name'],
            'Society Lat': societies_df['latitude'],
            'Society Lon': societies_df['longitude'],
            'Nearest Dark Store': darkstores_df.iloc[idx]['Store name as per projects'].values,
            'Distance (km)': np.round(dists_km, 2)
        })

        st.success("Mapping complete!")

        # Filters
        with st.expander("🔎 Filter Results"):
            selected_store = st.multiselect("Select Dark Stores", options=result_df['Nearest Dark Store'].unique(), default=None)
            max_distance = st.slider("Maximum Distance (km)", min_value=0.0, max_value=float(result_df['Distance (km)'].max()), value=float(result_df['Distance (km)'].max()), step=0.1)
            filtered_df = result_df.copy()
            if selected_store:
                filtered_df = filtered_df[filtered_df['Nearest Dark Store'].isin(selected_store)]
            filtered_df = filtered_df[filtered_df['Distance (km)'] <= max_distance]

        st.write("### Filtered Mapping Result")
        st.dataframe(filtered_df)

        # Grouping option
        with st.expander("🔍 Group by Store or City"):
            tab1, tab2 = st.tabs(["By Store", "By City"])
            with tab1:
                grouped_store = filtered_df.groupby('Nearest Dark Store').size().reset_index(name='Total Societies')
                st.dataframe(grouped_store)
            with tab2:
                grouped_city = filtered_df.groupby('City').size().reset_index(name='Total Societies')
                st.dataframe(grouped_city)

        # CSV export
        csv_data = filtered_df.to_csv(index=False).encode()
        st.download_button(
            label="📥 Download Filtered Result as CSV",
            data=csv_data,
            file_name="filtered_society_store_mapping.csv",
            mime="text/csv"
        )
