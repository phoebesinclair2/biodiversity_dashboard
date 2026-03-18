import pandas as pd
import duckdb
from pathlib import Path
from .clean_data import clean_observations

print("load_data.py started")
print(f"__name__ = {__name__}")

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_PATH = PROJECT_ROOT / "data" / "raw" / "observations.csv"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "observations_clean.parquet"
DB_PATH = PROJECT_ROOT / "data" / "biodiversity.duckdb"


def get_conn(reset: bool = False):
    if reset and DB_PATH.exists():
        DB_PATH.unlink()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def run_pipeline():
    df = pd.read_csv(RAW_PATH)
    df_clean = clean_observations(df)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_parquet(PROCESSED_PATH, index=False)

    conn = get_conn(reset=True)

    conn.execute("""
        CREATE TABLE observations AS
        SELECT * FROM read_parquet(?)
    """, [str(PROCESSED_PATH)])

    conn.close()

    print("Pipeline complete")
    print(f"Rows loaded: {len(df_clean):,}")
    print(f"Saved parquet: {PROCESSED_PATH}")
    print(f"Saved database: {DB_PATH}")


if __name__ == "__main__":
    run_pipeline()