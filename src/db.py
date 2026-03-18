from __future__ import annotations

from pathlib import Path
import re
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "biodiversity.duckdb"

def get_conn(read_only: bool = False) -> duckdb.DuckDBPyConnection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH), read_only=read_only)

def init_db() -> None:
    with get_conn() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                dataset_name TEXT PRIMARY KEY,
                source_file TEXT,
                loaded_at TIMESTAMP DEFAULT now()
            );
        """)

def safe_table_name(filename: str) -> str:
    name = Path(filename).stem.lower()
    name = re.sub(r"[^a-z0-9_]+", "_", name)
    return name

def load_csv_folder(folder: str = "data") -> list[str]:
    created = []
    data_dir = Path(folder)
    csv_files = sorted(data_dir.glob("*.csv"))

    if not csv_files:
        return created

    with get_conn() as con:
        for csv_path in csv_files:
            table = safe_table_name(csv_path.name)

            con.execute(f'''
                CREATE OR REPLACE TABLE "{table}" AS
                SELECT * FROM read_csv_auto('{csv_path.as_posix()}');
            ''')

            con.execute("""
                INSERT OR REPLACE INTO datasets(dataset_name, source_file)
                VALUES (?, ?);
            """, [table, str(csv_path)])

            created.append(table)

    return created