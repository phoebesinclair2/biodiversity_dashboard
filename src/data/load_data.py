import pandas as pd
from pathlib import Path
from .clean_data import clean_observations

RAW_PATH = Path("data/raw/observations.csv")
PROCESSED_PATH = Path("data/processed/observations_clean.parquet")

def run_pipeline():
    df = pd.read_csv(RAW_PATH)
    df_clean = clean_observations(df)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_parquet(PROCESSED_PATH, index=False)

if __name__ == "__main__":
    run_pipeline()