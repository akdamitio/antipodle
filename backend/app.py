
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, MultiPolygon, shape
from shapely.ops import unary_union
import datetime
import hashlib
import json
from shapely.geometry import mapping
import streamlit as st




# Load data
world = gpd.read_file("antipodle/backend/ne_10m_admin_0_countries.shp")
world = world.to_crs(epsg=4326)
iso_df = pd.read_csv("antipodle/backend/ISO Codes.csv")  # Must contain columns: 'Code' and 'Name'

# Merge to add ISO Code to world GeoDataFrame
world = world.merge(iso_df, left_on="ADMIN", right_on="Name")

# Determine today's index using local date and optional seed
def get_daily_country_index(date_str, mode='normal'):
    salted = date_str + ("_hard" if mode == 'hard' else "_normal")
    hashed = hashlib.md5(salted.encode()).hexdigest()
    return int(hashed, 16) % len(world)

# Antipode transform
def get_antipode_geometry(geom):
    def flip_coords(coords):
        return [[(lng + 180) % 360 - 180, -lat] for lng, lat in coords]

    if geom.geom_type == 'Polygon':
        return Polygon(flip_coords(geom.exterior.coords))
    elif geom.geom_type == 'MultiPolygon':
        return MultiPolygon([
            Polygon(flip_coords(poly.exterior.coords))
            for poly in geom.geoms
        ])
    else:
        raise ValueError("Unsupported geometry type for antipode transformation.")

# Main daily logic
def get_antipodle_data(date: datetime.date = None, mode='normal'):
    if date is None:
        date = datetime.date.today()
    date_str = date.isoformat()

    idx = get_daily_country_index(date_str, mode)
    origin = world.iloc[idx]
    origin_geom = origin.geometry
    origin_iso = origin["Code"]
    origin_name = origin["Name"]

    # Antipode of origin country
    antipode_geom = get_antipode_geometry(origin_geom)

    # Determine intersecting countries
    correct_countries = world[world.geometry.intersects(antipode_geom)].copy()
    correct_names = correct_countries["Name"].tolist()
    correct_codes = correct_countries["Code"].tolist()

    # Bonus country (smallest area)
    correct_countries["area"] = correct_countries.geometry.area
    bonus_country = correct_countries.sort_values("area").iloc[0]

    return {
        "origin_name": origin_name,
        "origin_code": origin_iso.lower(),  # For Teuteuf SVG use
        "origin_geometry": mapping(origin_geom),
        "antipode_geometry": mapping(antipode_geom),
        "correct_names": correct_names,
        "correct_codes": [code.lower() for code in correct_codes],
        "bonus_name": bonus_country["Name"],
        "bonus_code": bonus_country["Code"].lower()
    }

st.set_page_config(layout="wide")
st.markdown("<h1>Backend API for Antipodle</h1>", unsafe_allow_html=True)
st.json(get_antipodle_data())
