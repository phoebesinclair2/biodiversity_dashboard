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

def assign_color(taxa):
    if taxa == "Plants":
        return [141, 211, 199] # Green
    elif taxa == "Birds":
        return [190, 186, 218] # Blue
    elif taxa == "Insects":
        return [255, 255, 179] # Light Yellow
    elif taxa == "Mammals":
        return [251, 128, 114] # Salmon
    elif taxa == "Funghi":
        return [128, 177, 211] # Lavender
    else:
        return [200, 200, 200]  # fallback

df["color"] = df["taxa"].apply(assign_color)

    return df