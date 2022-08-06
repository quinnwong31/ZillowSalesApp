import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from pathlib import Path
import shutil
import hvplot.pandas

from zillow_fn import get_regions, load_zillow_region_data, load_zillow_sales_data, load_county_coordinates, merge_zillow_data, merge_zillow_county_coordinate_data

st.set_page_config(layout="wide")
st.title('Zillow Sales')

# Load data
region_df = load_zillow_region_data(10000)
sales_df = load_zillow_sales_data(10000, region_df)
county_coordinates_df = load_county_coordinates()
zillow_df = merge_zillow_data(region_df, sales_df)

# Merge data
master_df = merge_zillow_county_coordinate_data(
    zillow_df, county_coordinates_df)

county_df = master_df.groupby(["state", "county"], as_index=False).mean()

# Divide price by 1000 so that it looks better on map.
county_df["value"] = county_df["value"] / 1000

# Create dataframe
df = pd.DataFrame(
    county_df,
    columns=['county', 'state', 'region_id', 'value', 'latitude', 'longitude'])

# Tooltip to display county data
tooltip = {
    "html": "County: {county}</br> State: {state}</br>  Mean Sales: ${value}</br> " +
    " Type: {type} </br> Latitude: {latitude} </br> Longitude: {longitude} </br> "
}

# 3D Map
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=30.00,
        longitude=-99,
        zoom=4.8,
        pitch=50,
        height=1300,
        width=2000,
    ),
    tooltip=tooltip,
    layers=[
        pdk.Layer(
            'ColumnLayer',
            data=df,
            get_position='[longitude, latitude]',
            radius=10000,
            elevation_scale=200,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
            get_color='[200, 30, 0, 160]',
            get_elevation='value'
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position='[longitude, latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=10000,
        ),
    ],
))
