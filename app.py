import streamlit as st
import pandas as pd
import pydeck as pdk
from src.db import init_db, get_conn
from src.styles.css import load_css

st.set_page_config(
    page_title="Biodiversity Insights",
    page_icon="🌿",
    layout="wide",
)
st.markdown(load_css(), unsafe_allow_html=True)

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

# Format date
if "observed_on" in map_df.columns:
    map_df["observed_on_display"] = pd.to_datetime(
        map_df["observed_on"], errors="coerce"
    ).dt.strftime("%d %b %Y")

# Format time (if available)
if "time_observed_at" in map_df.columns:
    map_df["time_observed_display"] = pd.to_datetime(
        map_df["time_observed_at"], errors="coerce"
    ).dt.strftime("%H:%M")

# Clean username (fallback if missing)
if "user_name" in map_df.columns:
    map_df["user_display"] = map_df["user_name"].fillna("Unknown observer")


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
                "text": (
                    "Taxa: {iconic_taxon_name}\n"
                    "Species: {scientific_name}\n"
                    "Date: {observed_on_display}\n"
                    "Time: {time_observed_display}\n"
                    "Observer: {user_display}"
                )
            }
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
# Yearly Metrics
st.subheader("Yearly Metrics")

# Ensure observed_on is datetime for yearly metrics
df["observed_on"] = pd.to_datetime(df["observed_on"], errors="coerce")
df["year"] = df["observed_on"].dt.year

# Calculate species richness by year
richness_by_year = (
    df.groupby("year")["scientific_name"]
    .nunique()
    .reset_index(name="species_richness")
)

# Calculate observation counts by year
counts_by_year = (
    df.groupby("year")
    .size()
    .reset_index(name="observation_count")
)

yearly_metrics = pd.merge(richness_by_year, counts_by_year, on="year")

yearly_metrics = yearly_metrics.sort_values("year")
yearly_metrics

import matplotlib.pyplot as plt

# Ensure year is clean
yearly_metrics["year"] = yearly_metrics["year"].astype(int)

st.subheader("Yearly Metrics")

col1, col2 = st.columns(2)

# -------------------
# Observation Count
# -------------------
with col1:
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    
    ax1.bar(yearly_metrics["year"], yearly_metrics["observation_count"])
    ax1.set_title("Observation Count by Year")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Total Observations")
    ax1.set_xticks(yearly_metrics["year"])
    
    plt.tight_layout()
    st.pyplot(fig1)
    st.caption(
    "Observation count represents the total number of biodiversity records collected each year. "
    "This metric reflects sampling effort, which can influence other measures such as species richness."
)

# -------------------
# Species Richness
# -------------------
with col2:
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    
    ax2.bar(yearly_metrics["year"], yearly_metrics["species_richness"])
    ax2.set_title("Species Richness by Year")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Unique Species")
    ax2.set_xticks(yearly_metrics["year"])
    
    plt.tight_layout()
    st.pyplot(fig2)
    st.caption(
    "Species richness is calculated as the number of unique species (based on scientific name) recorded each year. "
    "It provides a measure of biodiversity, but should be interpreted alongside observation counts due to variation in sampling effort."
)

df["year"] = df["observed_on"].dt.year
df["month"] = df["observed_on"].dt.month

st.subheader("Advanced Biodiversity Metrics")

st.markdown("#### Effort-normalised Richness")

col1, col2 = st.columns([1, 1])

with col1:
    yearly_metrics["richness_per_100_obs"] = (
        yearly_metrics["species_richness"] / yearly_metrics["observation_count"]
    ) * 100

    yearly_metrics["year"] = yearly_metrics["year"].astype(int)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(yearly_metrics["year"], yearly_metrics["richness_per_100_obs"])
    ax.set_title("Species Richness per 100 Observations")
    ax.set_xlabel("Year")
    ax.set_ylabel("Richness per 100 Observations")
    ax.set_xticks(yearly_metrics["year"])
    plt.tight_layout()
    st.pyplot(fig)
    st.caption(
        "Effort-normalised richness shows the number of unique species recorded per 100 observations. "
        "This metric helps account for differences in sampling effort, providing a more comparable measure of biodiversity across years."
    )

st.subheader("Seasonality")

df["month"] = df["observed_on"].dt.month

seasonality = (
    df.groupby("month")["scientific_name"]
    .nunique()
    .reset_index(name="species_richness")
)

month_labels = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}
seasonality["month_name"] = seasonality["month"].map(month_labels)

fig, ax = plt.subplots(figsize=(8, 3))
ax.bar(seasonality["month_name"], seasonality["species_richness"])
ax.set_title("Species Richness by Month")
ax.set_xlabel("Month")
ax.set_ylabel("Unique Species")
plt.tight_layout()

st.pyplot(fig)
st.caption(
    "Seasonality illustrates how species richness varies throughout the year. "
    "This helps identify periods of higher biodiversity, which may reflect ecological patterns such as breeding seasons or increased biological activity."
)

st.subheader("Taxa-specific Trends")

taxa_trends = (
    df.groupby(["year", "iconic_taxon_name"])["scientific_name"]
    .nunique()
    .reset_index(name="species_richness")
)

taxa_pivot = taxa_trends.pivot(
    index="year",
    columns="iconic_taxon_name",
    values="species_richness"
).fillna(0)

taxa_pivot.index = taxa_pivot.index.astype(int)

st.line_chart(taxa_pivot)
st.caption(
    "Taxa-specific trends show how species richness changes over time for different taxonomic groups. "
    "This allows comparison of biodiversity patterns across groups, highlighting differences in ecological dynamics or observation behaviour."
)
