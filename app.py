import streamlit as st
import pandas as pd
from src.db import init_db, get_conn

st.set_page_config(
    page_title="Biodiversity Insights",
    page_icon="🌿",
    layout="wide",
)

# Cache database setup and data loading to speed up app performance

@st.cache_resource
def setup_database():
    init_db()
    return True

@st.cache_data
def load_observations():
    with get_conn(read_only=True) as con:
        return con.execute("SELECT * FROM observations").df()

# Initialise DB
setup_database()

# Load data
try:
    df = load_observations()
except Exception:
    df = pd.DataFrame()

st.title("🌿 Biodiversity Insights Dashboard")

if df.empty:
    st.warning("No observations table found. Run your data pipeline first.")
    st.stop()

# Filter by taxa group
st.subheader("Filters")

taxa_options = ["All"] + sorted(df["iconic_taxon_name"].dropna().unique().tolist())

selected_taxa = st.selectbox(
    "Filter by taxa group",
    taxa_options
)

if selected_taxa != "All":
    df = df[df["iconic_taxon_name"] == selected_taxa]

# Summary Metrics

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Observations", f"{len(df):,}")

with col2:
    st.metric("Unique Species", df["scientific_name"].nunique())

with col3:
    st.metric("Taxa Groups", df["iconic_taxon_name"].nunique())

# Data Preview

st.subheader("Sample Data")
st.dataframe(df.head(50), use_container_width=True)

# Observation Map

st.subheader("Observation Map")

import pydeck as pdk

st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=df["latitude"].mean(),
        longitude=df["longitude"].mean(),
        zoom=10,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position='[longitude, latitude]',
            get_radius=50,
            pickable=True,
        )
    ],
))