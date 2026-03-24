import streamlit as st
import pandas as pd
import pydeck as pdk
from src.db import init_db, get_conn

st.set_page_config(
    page_title="Biodiversity Insights",
    page_icon="🌿",
    layout="wide",
)

# Define map colours based on taxa group
def get_color_map():
    return {
        "Plantae": [141, 211, 199],
        "Aves": [190, 186, 218],
        "Insecta": [255, 255, 179],
        "Mammalia": [251, 128, 114],
        "Fungi": [128, 177, 211],
        "Amphibia": [179, 222, 105],
        "Reptilia": [252, 205, 229],
        "Actinopterygii": [217, 217, 217],
        "Arachnida": [204, 235, 197],
        "Mollusca": [255, 237, 111],
    }

def assign_color(taxa_group):
    return get_color_map().get(taxa_group, [200, 200, 200])

# Cache database setup and data loading to speed up performance
@st.cache_resource
def setup_database():
    init_db()
    return True


@st.cache_data
def load_observations():
    with get_conn(read_only=True) as con:
        df = con.execute("SELECT * FROM observations").df()

    # Add colour column in pandas, not in the DB
    if "iconic_taxon_name" in df.columns:
        df["color"] = df["iconic_taxon_name"].apply(assign_color)

    return df

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
    df = df[df["iconic_taxon_name"] == selected_taxa].copy()

# Rebuild colours after filtering
if "iconic_taxon_name" in df.columns:
    df["color"] = df["iconic_taxon_name"].apply(assign_color)

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
st.dataframe(df.head(50), width="stretch")

# Observation Map
st.subheader("Observation Map")

# Ensure valid coordinates before mapping
map_df = df.dropna(subset=["latitude", "longitude"]).copy()

if map_df.empty:
    st.warning("No valid coordinates available to display on the map.")
else:
    st.pydeck_chart(
        pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=map_df["latitude"].mean(),
                longitude=map_df["longitude"].mean(),
                zoom=15,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=map_df,
                    get_position='[longitude, latitude]',
                    get_fill_color="color",
                    get_radius=8,
                    pickable=True,
                    opacity=0.9,
                    stroked=True,
                    filled=True,
                    line_width_min_pixels=1,
                )
            ],
            tooltip={
                "text": "Taxa: {iconic_taxon_name}\nSpecies: {scientific_name}"
            },
        )
    )
    st.markdown("### Map Legend")

color_map = get_color_map()

# Only show taxa that exist in current filtered data
present_taxa = sorted(df["iconic_taxon_name"].dropna().unique())

cols = st.columns(len(present_taxa))

for col, taxa in zip(cols, present_taxa):
    rgb = color_map.get(taxa, [200, 200, 200])
    hex_color = '#%02x%02x%02x' % tuple(rgb)

    col.markdown(
        f"""
        <div style="display: flex; align-items: center;">
            <div style="
                width: 15px;
                height: 15px;
                background-color: {hex_color};
                border-radius: 50%;
                margin-right: 6px;
                border: 1px solid #ccc;
            "></div>
            <span style="font-size: 14px;">{taxa}</span>
        </div>
        """,
        unsafe_allow_html=True
    )