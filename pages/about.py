import streamlit as st

st.title("About this Dashboard")

st.markdown("""
## Project Overview

This dashboard was developed as part of an MSc Data Science research project exploring how biodiversity data from heterogeneous sources can be integrated, analysed, and visualised to support interpretation and decision-making.

The application demonstrates how citizen science observations can be transformed into meaningful biodiversity indicators through the use of a structured data pipeline, an analytical database, and an interactive dashboard interface.

The project focuses on observations collected from a Forestry Commission site using data sourced from the
**[iNaturalist](https://www.inaturalist.org/)** platform.  
The dataset used in this prototype contains approximately **867 observations representing 331 species across nine taxonomic groups collected over six years**.

---

## Biodiversity Indicators

The dashboard presents several biodiversity indicators commonly used in ecological monitoring:

**Observation Count**  
Total number of biodiversity observations recorded. This metric reflects sampling effort.

**Species Richness**  
The number of unique species recorded within the dataset.

**Effort-Normalised Richness**  
Species richness adjusted relative to the number of observations. This helps account for differences in sampling effort between years.

**Shannon Diversity Index**  
A widely used ecological diversity index combining species richness and species evenness to provide a more comprehensive measure of biodiversity.

**Seasonality**  
Monthly patterns in species richness, which may reflect ecological cycles such as breeding seasons or periods of higher biological activity.

**Taxa-Specific Trends**  
Changes in species richness over time for different taxonomic groups.

---

## Data Sources

Biodiversity observations used in this dashboard were obtained from the
**[iNaturalist](https://www.inaturalist.org/)** platform, a global citizen science initiative that enables individuals to record and share biodiversity observations.

The dataset represents publicly available observations collected within the selected study area.

---

## Limitations

Citizen science datasets provide valuable biodiversity insights but may contain several limitations, including:

- Uneven geographic sampling coverage  
- Taxonomic observation bias  
- Opportunistic sampling behaviour  
- Variation in observation effort across time

For these reasons, the indicators presented in this dashboard should be interpreted as **exploratory measures of biodiversity patterns rather than definitive ecological assessments**.

---

## Author

This dashboard was developed by **Phoebe Sinclair** as part of an MSc Data Science project investigating biodiversity data integration and dashboard-based visualisation approaches.

---

## Source Code

The full source code for this dashboard is available on GitHub:

[https://github.com/phoebesinclair2/biodiversity_dashboard](https://github.com/phoebesinclair2/biodiversity_dashboard)

The repository includes the data pipeline, database setup, and dashboard application used to generate the visualisations presented here.            

The application is implemented in Python using the Streamlit framework with DuckDB used as an embedded analytical database.
""")