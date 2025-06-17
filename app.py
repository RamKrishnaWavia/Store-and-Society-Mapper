import streamlit as st
import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371
    return c * r

st.title("Society to Nearest Dark Store Mapper")

uploaded_file = st.file_uploader("Upload Excel File with 'Societies' and 'Dark Stores' sheets", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    societies_df = xls.parse('Societies')
    darkstores_df = xls.parse('Dark Stores')

    results = []
    for _, soc_row in societies_df.iterrows():
        min_dist = float('inf')
        nearest_store = None

        for _, store_row in darkstores_df.iterrows():
            dist = haversine(soc_row['latitude'], soc_row['longitude'], store_row['Latitude'], store_row['Longitude'])
            if dist < min_dist:
                min_dist = dist
                nearest_store = store_row['Store name as per projects']

        results.append({
            'Society Name': soc_row['Society_name'],
            'Society Lat': soc_row['latitude'],
            'Society Lon': soc_row['longitude'],
            'Nearest Dark Store': nearest_store,
            'Distance (km)': round(min_dist, 2)
        })

    result_df = pd.DataFrame(results)
    st.write("### Mapping Result")
    st.dataframe(result_df)
    st.download_button("Download Result as CSV", result_df.to_csv(index=False), "society_store_mapping.csv")
