
from __future__ import annotations

from pathlib import Path
import re
import duckdb

# defines the path to the DuckDB database file
DB_PATH = Path("data") / "biodiversity.duckdb" 

# Open DuckDB connection 
def get_conn(read_only: bool = False) -> duckdb.DuckDBPyConnection: # Allow db file to be write enabled for data loading. 
    
    DB_PATH.parent.mkdir(parents=True, exist_ok=True) # ensure the data folder exists
    return duckdb.connect(str(DB_PATH), read_only=read_only) # connected to DuckDB database file or create if non existent

#Create tables if they don't exist to intialise the database. 
def init_db() -> None:
    with get_conn() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                dataset_name TEXT PRIMARY KEY,
                source_file TEXT,
                loaded_at TIMESTAMP DEFAULT now()
            );
        """)
import re

def safe_table_name(filename: str) -> str:
    # fungi_counts.csv -> fungi_counts
    name = Path(filename).stem.lower()
    name = re.sub(r"[^a-z0-9_]+", "_", name)
    return name

def load_csv_folder(folder: str = "data") -> list[str]:
    """
    Load all CSV files in /data into DuckDB tables using CREATE OR REPLACE TABLE.
    Return list of created table names.
    """
    created = []
    data_dir = Path(folder)
    csv_files = sorted(data_dir.glob("*.csv"))

    if not csv_files:
        return created

    with get_conn() as con:
        for csv_path in csv_files:
            table = safe_table_name(csv_path.name)

            # Create table directly from CSV (DuckDB reads headers + types)
            con.execute(f"""
                CREATE OR REPLACE TABLE {table} AS
                SELECT * FROM read_csv_auto('{csv_path.as_posix()}');
            """)

            con.execute("""
                INSERT OR REPLACE INTO datasets(dataset_name, source_file)
                VALUES (?, ?);
            """, [table, str(csv_path)])

            created.append(table)

    return created