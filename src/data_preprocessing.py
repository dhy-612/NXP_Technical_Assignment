"""Reusable World Bank data preprocessing for the NXP assignment."""

from pathlib import Path
from typing import Dict, Tuple

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

START_YEAR = 1960
END_YEAR = 2023
YEARS = list(range(START_YEAR, END_YEAR + 1))

ID_COLUMNS = [
    "Country Name",
    "Country Code",
    "Indicator Name",
    "Indicator Code",
]

FOLDER_MAP: Dict[str, str] = {
    "LifeExp_Total": "API_SP.DYN.LE00.IN_DS2_en_csv_v2_408",
    "LifeExp_Male": "API_SP.DYN.LE00.MA.IN_DS2_en_csv_v2_189",
    "LifeExp_Female": "API_SP.DYN.LE00.FE.IN_DS2_en_csv_v2_34008",
    "Death_Rate": "API_SP.DYN.CDRT.IN_DS2_en_csv_v2_33278",
    "Fertility_Rate": "API_SP.DYN.TFRT.IN_DS2_EN_csv_v2_33381",
}


def find_main_csv(folder: Path) -> Path:
    """Return the primary World Bank data CSV in a raw indicator folder."""
    csv_files = [
        path
        for path in folder.glob("*.csv")
        if not path.name.startswith("Metadata_")
    ]

    if len(csv_files) != 1:
        raise FileNotFoundError(
            f"Expected exactly one main CSV in {folder}, found {len(csv_files)}."
        )

    return csv_files[0]


def load_indicator(folder: Path) -> pd.DataFrame:
    """Load one World Bank indicator and reshape it to long format."""
    main_file = find_main_csv(folder)

    df = pd.read_csv(main_file, skiprows=4)
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]

    year_columns = [str(year) for year in YEARS]
    required_columns = ID_COLUMNS + year_columns

    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            f"{main_file.name} is missing expected columns: {missing_columns}"
        )

    df = df[required_columns].copy()

    long_df = df.melt(
        id_vars=ID_COLUMNS,
        value_vars=year_columns,
        var_name="Year",
        value_name="Value",
    )

    long_df["Year"] = pd.to_numeric(
        long_df["Year"], errors="coerce"
    ).astype(int)
    long_df["Value"] = pd.to_numeric(
        long_df["Value"], errors="coerce"
    )

    duplicate_count = long_df.duplicated(
        ["Country Code", "Year"]
    ).sum()
    if duplicate_count:
        raise ValueError(
            f"Found {duplicate_count} duplicate Country Code-Year rows in "
            f"{main_file.name}."
        )

    return long_df


def load_country_metadata(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Load country Region and IncomeGroup metadata."""
    first_folder = raw_dir / next(iter(FOLDER_MAP.values()))
    metadata_files = list(first_folder.glob("Metadata_Country_*.csv"))

    if not metadata_files:
        raise FileNotFoundError(
            f"No country metadata CSV found in {first_folder}."
        )

    metadata = pd.read_csv(metadata_files[0])
    required = ["Country Code", "Region", "IncomeGroup"]
    missing = [column for column in required if column not in metadata.columns]

    if missing:
        raise ValueError(
            f"Country metadata is missing required columns: {missing}"
        )

    metadata = metadata[required].copy()

    if metadata["Country Code"].duplicated().any():
        raise ValueError("Country metadata contains duplicate Country Codes.")

    return metadata


def build_datasets(
    raw_dir: Path = RAW_DIR,
    processed_dir: Path = PROCESSED_DIR,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Build and save master_dataset.csv and classified_dataset.csv."""
    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)

    indicator_data = {}

    for indicator_name, folder_name in FOLDER_MAP.items():
        folder = raw_dir / folder_name

        if not folder.exists():
            raise FileNotFoundError(f"Raw indicator folder not found: {folder}")

        indicator_data[indicator_name] = load_indicator(folder)

    master_df = indicator_data["LifeExp_Total"].rename(
        columns={"Value": "LifeExp_Total"}
    )[["Country Name", "Country Code", "Year", "LifeExp_Total"]].copy()

    for indicator_name in [
        "LifeExp_Male",
        "LifeExp_Female",
        "Death_Rate",
        "Fertility_Rate",
    ]:
        indicator_df = indicator_data[indicator_name].rename(
            columns={"Value": indicator_name}
        )[["Country Code", "Year", indicator_name]]

        master_df = master_df.merge(
            indicator_df,
            on=["Country Code", "Year"],
            how="left",
            validate="one_to_one",
        )

    master_df = master_df.merge(
        load_country_metadata(raw_dir),
        on="Country Code",
        how="left",
        validate="many_to_one",
    )

    master_df["Gender_Gap"] = (
        master_df["LifeExp_Female"] - master_df["LifeExp_Male"]
    )

    master_df = master_df[
        [
            "Country Name",
            "Country Code",
            "Region",
            "IncomeGroup",
            "Year",
            "LifeExp_Total",
            "LifeExp_Male",
            "LifeExp_Female",
            "Death_Rate",
            "Fertility_Rate",
            "Gender_Gap",
        ]
    ].sort_values(["Country Code", "Year"]).reset_index(drop=True)

    if master_df.duplicated(["Country Code", "Year"]).any():
        raise ValueError(
            "Master dataset contains duplicate Country Code-Year rows."
        )

    classified_df = master_df[master_df["IncomeGroup"].notna()].copy()

    master_df.to_csv(processed_dir / "master_dataset.csv", index=False)
    classified_df.to_csv(
        processed_dir / "classified_dataset.csv", index=False
    )

    return master_df, classified_df


if __name__ == "__main__":
    master, classified = build_datasets()
    print(f"Master dataset: {master.shape}")
    print(f"Classified dataset: {classified.shape}")
