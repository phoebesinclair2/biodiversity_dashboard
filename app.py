import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt

from src.db import init_db, get_conn
from src.styles.css import load_css


st.set_page_config(
    page_title="Biodiversity Insights",
    page_icon="🌿",
    layout="wide",
)
st.markdown(load_css(), unsafe_allow_html=True)

# Display order for charts and legends
taxa_order = [
    "Birds",
    "Mammals",
    "Reptiles",
    "Amphibians",
    "Insects",
    "Spiders",
    "Molluscs",
    "Ray-finned Fishes",
    "Plants",
    "Fungi",
]


# Define map colours based on common taxa group
def get_color_map():
    return {
        "Plants": [141, 211, 199],
        "Birds": [190, 186, 218],
        "Insects": [255, 255, 179],
        "Mammals": [251, 128, 114],
        "Fungi": [128, 177, 211],
        "Amphibians": [179, 222, 105],
        "Reptiles": [252, 205, 229],
        "Ray-finned Fishes": [217, 217, 217],
        "Spiders": [204, 235, 197],
        "Molluscs": [255, 237, 111],
    }


def assign_color(taxa_group):
    return get_color_map().get(taxa_group, [200, 200, 200])


def normalise_color(rgb):
    return [c / 255 for c in rgb]


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
    if "taxa_common" in df.columns:
        df["color"] = df["taxa_common"].apply(assign_color)

    return df


# Initialise DB
setup_database()

# Load data
try:
    df = load_observations()
except Exception:
    df = pd.DataFrame()

st.title("🌿 Biodiversity Insights Dashboard")

st.warning(
    """
⚠️ **Prototype Dashboard – Research Project**

This dashboard was developed as part of an MSc Data Science research project and is intended as a
demonstration of biodiversity data integration and visualisation techniques.

The visualisations are based on publicly available **citizen science observations from iNaturalist**.
Such data may contain biases including uneven geographic coverage, taxonomic imbalance, and
opportunistic sampling behaviour.

Observations should therefore **not be interpreted as a complete representation of biodiversity
or species abundance**, but as an exploratory dataset used to demonstrate analytical methods.
"""
)

if df.empty:
    st.warning("No observations table found. Run your data pipeline first.")
    st.stop()

# Ensure observed_on is datetime before using .dt
if "observed_on" in df.columns:
    df["observed_on"] = pd.to_datetime(df["observed_on"], errors="coerce")

# Dataset Summary
st.subheader("Dataset Summary")
st.caption("Metrics based on the complete dataset.")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Observations",
    f"{len(df):,}",
)

col2.metric(
    "Species",
    f"{df['scientific_name'].nunique():,}"
    if "scientific_name" in df.columns
    else "N/A",
)

col3.metric(
    "Taxa Groups",
    f"{df['taxa_common'].nunique():,}"
    if "taxa_common" in df.columns
    else "N/A",
)

col4.metric(
    "Years Covered",
    f"{df['observed_on'].dt.year.nunique():,}"
    if "observed_on" in df.columns
    else "N/A",
)

st.divider()

# Filter by taxa group
taxa_options = sorted(df["taxa_common"].dropna().unique().tolist())

selected_taxa = st.multiselect(
    "Filter by taxa group",
    taxa_options,
    default=taxa_options,
)

if selected_taxa:
    df = df[df["taxa_common"].isin(selected_taxa)].copy()

# Rebuild colours after filtering
if "taxa_common" in df.columns:
    df["color"] = df["taxa_common"].apply(assign_color)

# Filtered Dataset Summary
st.subheader("Filtered Dataset Summary")
st.caption("Metrics update automatically based on the selected taxa filters.")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Observations",
    f"{len(df):,}",
)

col2.metric(
    "Species",
    f"{df['scientific_name'].nunique():,}"
    if "scientific_name" in df.columns
    else "N/A",
)

col3.metric(
    "Taxa Groups",
    f"{df['taxa_common'].nunique():,}"
    if "taxa_common" in df.columns
    else "N/A",
)

col4.metric(
    "Years Covered",
    f"{df['observed_on'].dt.year.nunique():,}"
    if "observed_on" in df.columns
    else "N/A",
)

# Data Preview
st.subheader("Data Preview (First 50 Rows)")
st.dataframe(df.head(50), width="stretch")

# Observation Map
st.subheader("Observation Map")

# Ensure valid coordinates before mapping
map_df = df.dropna(subset=["latitude", "longitude"]).copy()

# Format date
if "observed_on" in map_df.columns:
    map_df["observed_on_display"] = pd.to_datetime(
        map_df["observed_on"],
        errors="coerce",
    ).dt.strftime("%d %b %Y")

# Format time (if available)
if "time_observed_at" in map_df.columns:
    map_df["time_observed_display"] = pd.to_datetime(
        map_df["time_observed_at"],
        errors="coerce",
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
                    get_position="[longitude, latitude]",
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
                    "Taxa: {taxa_common}\n"
                    "Species: {scientific_name}\n"
                    "Date: {observed_on_display}\n"
                    "Time: {time_observed_display}\n"
                    "Observer: {user_display}"
                )
            },
        )
    )
    st.markdown("### Map Legend")

color_map = get_color_map()

# Only show taxa that exist in current filtered data
present_taxa = sorted(df["taxa_common"].dropna().unique())
st.caption("Spatial distribution of observations across the study site.")

if present_taxa:
    cols = st.columns(len(present_taxa))

    for col, taxa in zip(cols, present_taxa):
        rgb = color_map.get(taxa, [200, 200, 200])
        hex_color = "#%02x%02x%02x" % tuple(rgb)

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
            unsafe_allow_html=True,
        )

# Yearly Metrics
st.subheader("Yearly Metrics")

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
yearly_metrics["year"] = yearly_metrics["year"].astype(int)

# Shannon Diversity Index by year

def shannon_index(group):
    proportions = group["scientific_name"].value_counts(normalize=True)
    return -(proportions * np.log(proportions)).sum()

import numpy as np

shannon_by_year = (
    df.groupby("year")
    .apply(shannon_index)
    .reset_index(name="shannon_diversity")
)

yearly_metrics = pd.merge(yearly_metrics, shannon_by_year, on="year")

col1, col2 = st.columns(2)

# Observation Count
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

# Species Richness
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

df["month"] = df["observed_on"].dt.month

st.subheader("Advanced Biodiversity Metrics")
st.caption(
    "These indicators provide additional ecological insight beyond simple species counts."
)
st.markdown("#### Effort-normalised Richness")

col1, col2 = st.columns([1, 1])

with col1:
    yearly_metrics["richness_per_100_obs"] = (
        yearly_metrics["species_richness"] / yearly_metrics["observation_count"]
    ) * 100

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

with col2:
    fig, ax = plt.subplots(figsize=(6, 4))

    ax.plot(
        yearly_metrics["year"],
        yearly_metrics["shannon_diversity"],
        marker="o",
        linewidth=2
    )

    ax.set_title("Shannon Diversity Index by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Shannon Diversity (H')")
    ax.set_xticks(yearly_metrics["year"])

    plt.tight_layout()
    st.pyplot(fig)

    st.caption(
        "The Shannon Diversity Index measures biodiversity by combining species richness "
        "and species evenness. Higher values indicate a more diverse ecological community "
        "where species are more evenly distributed."
    )

st.subheader("Seasonality")

seasonality = (
    df.groupby("month")["scientific_name"]
    .nunique()
    .reset_index(name="species_richness")
)

month_labels = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
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

# Taxa-specific trends (interactive)
st.subheader("Taxa-specific Trends")

color_map = get_color_map()

# Build dataset
taxa_trends = (
    df.groupby(["year", "taxa_common"])["scientific_name"]
    .nunique()
    .reset_index(name="species_richness")
)

taxa_pivot = taxa_trends.pivot(
    index="year",
    columns="taxa_common",
    values="species_richness",
).fillna(0)

taxa_pivot.index = taxa_pivot.index.astype(int)

# Order taxa by preferred display order where possible
present_taxa = taxa_pivot.columns.tolist()
ordered_taxa = [taxa for taxa in taxa_order if taxa in present_taxa]
remaining_taxa = [taxa for taxa in present_taxa if taxa not in ordered_taxa]
taxa_options_for_plot = ordered_taxa + sorted(remaining_taxa)

# Default selection kept intentionally small to reduce visual clutter
default_taxa = [
    taxa
    for taxa in ["Plants", "Insects", "Birds", "Fungi"]
    if taxa in taxa_options_for_plot
]

selected_taxa = st.multiselect(
    "Choose taxa groups to display",
    options=taxa_options_for_plot,
    default=default_taxa if default_taxa else taxa_options_for_plot,
)

st.caption(
    "The chart opens with a small default selection of taxa groups to reduce "
    "visual clutter. Use the dropdown above to add or remove taxa and compare "
    "trends across the full dataset."
)

if selected_taxa:
    plot_df = taxa_pivot[selected_taxa]

    fig, ax = plt.subplots(figsize=(8, 3.5))

    for col in plot_df.columns:
        if col in color_map:
            base_color = normalise_color(color_map[col])
            color = [c * 0.8 for c in base_color]
        else:
            color = [0.4, 0.4, 0.4]

        ax.plot(
            plot_df.index,
            plot_df[col],
            marker="o",
            markersize=5,
            label=col,
            color=color,
            linewidth=2.5,
        )

    ax.set_title("Species Richness by Taxa Group Over Time")
    ax.set_xlabel("Year")
    ax.set_ylabel("Unique Species")
    ax.set_xticks(plot_df.index)
    ax.grid(True, alpha=0.2)

    ax.legend(
        title="Taxa",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=4,
        frameon=False,
    )

    plt.tight_layout()
    st.pyplot(fig)

    st.caption(
        "Taxa-specific trends show how species richness changes over time for "
        "selected taxonomic groups."
    )
else:
    st.info("Select at least one taxa group to display the chart.")