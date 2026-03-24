import pandas as pd

def clean_observations(df: pd.DataFrame) -> pd.DataFrame:
    # Convert dates
    df["observed_on"] = pd.to_datetime(df["observed_on"], errors="coerce")

    # Ensure coordinates are numeric
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # Drop missing key fields
    df = df.dropna(subset=["latitude", "longitude", "observed_on"])

    # Filter to research grade
    if "quality_grade" in df.columns:
        df = df[df["quality_grade"] == "research"]

    # Drop columns with little/no useful data or low dashboard value
    cols_to_drop = [
        "observed_on_string",
        "sound_url",
        "tag_list",
        "description",
        "oauth_application_id",
        "url",
        "image_url",
        "license",
        "private_place_guess",
        "private_latitude",
        "private_longitude",
        "geoprivacy",
        "taxon_geoprivacy",
        "positioning_method",
        "positioning_device",
        "species_guess",
    ]

    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

    return df