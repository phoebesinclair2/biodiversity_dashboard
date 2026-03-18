import pandas as pd

def clean_observations(df: pd.DataFrame) -> pd.DataFrame:
    # Convert dates
    df["observed_on"] = pd.to_datetime(df["observed_on"], errors="coerce")

    # Drop missing coordinates
    df = df.dropna(subset=["latitude", "longitude"])

    # Filter to research grade
    df = df[df["quality_grade"] == "research"]

    return df