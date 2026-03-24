# Biodiversity Dashboard 🌱

An interactive data dashboard for exploring biodiversity observations using data sourced from iNaturalist.
This project explores biodiversity trends using citizen science data, highlighting patterns in species richness and observation behaviour.
This project is part of an MSc Data Science portfolio and demonstrates data ingestion, cleaning, storage, and visualisation using modern Python tools.

## Features

- Interactive dashboard built with Streamlit
- Map-based visualisation of species observations
- Temporal analysis (species counts & richness over time)
- Data cleaning and transformation pipeline
- Local database storage using DuckDB
- Modular code structure for scalability

## Project Overview

This project ingests biodiversity observation data (primarily from iNaturalist), processes it into a structured format and presents it through an interactive dashboard.

The goal is to:
- Explore biodiversity trends over time
- Understand species richness in a defined area
- Provide a foundation for ecological analytics and decision-making

## Data Source

This project uses publicly available biodiversity observation data from:

iNaturalist - A global citizen science platform where users record and share biodiversity observations.

More info: https://www.inaturalist.org

## Data Licensing & Attribution

Data from iNaturalist is user-generated and licensed under various Creative Commons licenses.

See licensing details: https://help.inaturalist.org/

### Important Notes:
- Individual observations, images, and sounds may have **different licenses**
- If redistributing images or media, **you must attribute the original creator**
- If using only aggregated data (e.g. counts, summaries), dataset-level attribution is typically sufficient

Where possible, this project:
- Uses observation data for analysis
- Does not redistribute copyrighted images


## Tech Stack

- Python 3.12
- Streamlit (dashboard)
- DuckDB (local database)
- Pandas (data processing)
- PyDeck (mapping)


## Project Structure

```
biodiversity_dashboard/
│
├── app.py # Main Streamlit app
├── pages/ # Dashboard pages
├── src/
│   ├── clean_data.py       # Data cleaning pipeline
│   ├── db.py               # Database connection
│   └── ...                 # Additional modules
│
├── data/
│ ├── raw/ # Raw datasets
│ ├── processed/ # Cleaned data (e.g. parquet)
│ └── biodiversity.duckdb # Local database
│
├── requirements.txt
└── README.md
```

## Installation & Setup

### 1. Clone the repo

```bash
git clone https://github.com/phoebesinclair2/biodiversity_dashboard.git
cd biodiversity_dashboard
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate: 

Mac/Linux

```bash
source .venv/bin/activate
```

Windows
```bash
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```
## Future Improvements
- Add species richness metrics by year  
- Integrate environmental data (weather, habitat)  
- Improve map clustering and styling  
- Add filtering by taxa and geography  
- Deploy to cloud (Streamlit Cloud / AWS)

## Contributing
This is currently a personal/academic project, but suggestions and feedback are welcome.

## License

This project is licensed under the MIT License.
Note: This license applies to the code only. Data remains subject to iNaturalist licensing.

## Acknowledgements
iNaturalist community and contributors
GBIF (Global Biodiversity Information Facility)
Open-source Python ecosystem