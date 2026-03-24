import pandas as pd

def assign_color(taxa):
    color_map = {
        "Plants": [141, 211, 199],
        "Birds": [190, 186, 218],
        "Insects": [255, 255, 179],
        "Mammals": [251, 128, 114],
        "Fungi": [128, 177, 211],
    }
    return color_map.get(taxa, [200, 200, 200])


def clean_observations(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["observed_on"] = pd.to_datetime(df["observed_on"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    df = df.dropna(subset=["latitude", "longitude", "observed_on"])

    if "quality_grade" in df.columns:
        df = df[df["quality_grade"] == "research"].copy()

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

    if "taxa" in df.columns:
        df["color"] = df["taxa"].apply(assign_color)

    return df