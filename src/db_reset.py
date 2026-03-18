import duckdb
from pathlib import Path

DB_PATH = Path("data/biodiversity.duckdb")

def get_conn(reset=False):
    if reset and DB_PATH.exists():
        DB_PATH.unlink()  # deletes file

    return duckdb.connect(str(DB_PATH))