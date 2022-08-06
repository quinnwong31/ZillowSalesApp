from datetime import date
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import nasdaqdatalink
import requests
from pathlib import Path
import shutil
import hvplot.pandas
import datetime


def get_regions(regions):
    # A function to retrieve a dataframe of counties, zips, etc
    region_df = nasdaqdatalink.get_table('ZILLOW/REGIONS', region_type=regions)
    return region_df


@st.cache
def load_zillow_region_data(nrows):
    # A function to load and clean Zillow region dataat
    region_df = get_regions('county')
    region_df[["county", "state"]] = region_df["region"].str.split(
        ';', 1, expand=True)
    region_df["state"] = region_df["state"].str.split(';', 1, expand=True)[0]

    #
    # Clean up regions data
    # Remove ' County' so that we can match the Zillow data with Wikipedia data.
    region_df["county"] = region_df["county"].str.replace(" County", "")

    # Remove the leading blank space from the 'state' column.
    region_df["state"] = region_df['state'].str[1:]

    # Clean up region_id datatype.
    region_df['region_id'] = region_df['region_id'].astype(int)
    return region_df


@st.cache
def load_zillow_sales_data(nrows, region_df):
    # A function to load and clean Zillow sales data
    # Reading in Database
    zillow_data = pd.read_csv(
        Path('./data/zillow_sales.csv', parse_dates=['date'])
    )

    # Merge the Region dataframe with the Zillow sales data
    zillow_merge_df = pd.merge(region_df, zillow_data, on=['region_id'])

    # Check the merged Zillow data
    return zillow_merge_df


@st.cache
def load_county_coordinates():
    # Load county coordinates

    # Read in county data with coordinates
    county_coordinates_df = pd.read_csv(
        Path('./data/counties_w_coordinates.csv')
    )

    # Clean up data.
    # We need to rename the columns so that we can merge our Zillow data set
    # with the county coordinates data.   The dataframes will be merged against 'county' and 'state'.
    county_coordinates_df = county_coordinates_df.rename(
        columns={"County\xa0[2]": "county"})
    # county_coordinates_df = county_coordinates_df.rename(columns={"region" : "region"})
    county_coordinates_df = county_coordinates_df.rename(
        columns={"State": "state"})

    # Remove degrees
    county_coordinates_df["Latitude"] = county_coordinates_df["Latitude"].str.replace(
        "°", "")
    county_coordinates_df["Longitude"] = county_coordinates_df["Longitude"].str.replace(
        "°", "")

    # Remove + sign for Latitude and Longitude
    county_coordinates_df["Latitude"] = county_coordinates_df["Latitude"].str.replace(
        "+", "")
    county_coordinates_df["Longitude"] = county_coordinates_df["Longitude"].str.replace(
        "+", "")

    # Some of the data uses unicode hyphens which causes problems when trying to convert the Longitude and Latitude to float.
    county_coordinates_df["Latitude"] = county_coordinates_df["Latitude"].str.replace(
        '\U00002013', '-')
    county_coordinates_df["Longitude"] = county_coordinates_df["Longitude"].str.replace(
        '\U00002013', '-')

    # Convert Longitude and Latitude to float so we can display on the map.
    county_coordinates_df["Latitude"] = county_coordinates_df["Latitude"].astype(
        float)
    county_coordinates_df["Longitude"] = county_coordinates_df["Longitude"].astype(
        float)

    # Rename column names
    county_coordinates_df.rename(
        columns={'Latitude': 'latitude', 'Longitude': 'longitude'}, inplace=True)

    return county_coordinates_df


def merge_zillow_data(region_df, sales_df):
    # Merge Zillow region and sales data
    # Merge the Region dataframe with the Zillow sales data
    zillow_merge_df = pd.merge(region_df, sales_df, on=['region_id'])
    zillow_merge_df.rename(
        columns={'county_x': 'county', 'state_x': 'state'}, inplace=True)

    return zillow_merge_df


def merge_zillow_county_coordinate_data(zillow_df, county_coordinates_df):
    # Merge Zillow data with county coordinates
    # print(zillow_df.dtypes)

    # Merge the Zillow data and county coordinates data.
    master_df = pd.merge(
        zillow_df,
        county_coordinates_df,
        on=['state', 'county'])

    master_df["date"] = pd.to_datetime(master_df["date"])

    # Check the master data
    return master_df
