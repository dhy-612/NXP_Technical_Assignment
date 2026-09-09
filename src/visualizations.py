"""Required Plotly visualizations for the NXP assignment."""

from pathlib import Path
from typing import Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PROJECT_DIR = Path(__file__).resolve().parents[1]
VIS_DIR = PROJECT_DIR / "visualizations"

BUCKETS = ["Very low", "Low", "Medium", "High", "Very high"]


def plot_life_expectancy_by_income_group(
    classified_df: pd.DataFrame,
) -> go.Figure:
    """Create the required time-series chart by income group."""
    annual = (
        classified_df.dropna(subset=["LifeExp_Total"])
        .groupby(["IncomeGroup", "Year"], as_index=False)
        .agg(Avg_Life_Expectancy=("LifeExp_Total", "mean"))
    )

    fig = px.line(
        annual,
        x="Year",
        y="Avg_Life_Expectancy",
        color="IncomeGroup",
        title="Average Life Expectancy by Income Group (1960–2023)",
        labels={
            "Avg_Life_Expectancy": "Average Life Expectancy (years)",
            "Year": "Year",
            "IncomeGroup": "Income Group",
        },
    )

    fig.update_layout(
        hovermode="x unified",
        legend_title_text="Income Group",
    )

    return fig


def plot_2023_world_map(
    classified_df: pd.DataFrame,
) -> go.Figure:
    """Create a country-level choropleth for 2023 life expectancy."""
    map_df = classified_df[
        (classified_df["Year"] == 2023)
        & classified_df["IncomeGroup"].notna()
        & classified_df["LifeExp_Total"].notna()
    ].drop_duplicates("Country Code").copy()

    fig = px.choropleth(
        map_df,
        locations="Country Code",
        color="LifeExp_Total",
        hover_name="Country Name",
        hover_data={
            "Country Code": True,
            "LifeExp_Total": ":.1f",
            "IncomeGroup": True,
            "Region": True,
        },
        title="Life Expectancy at Birth by Country (2023)",
        labels={"LifeExp_Total": "Life Expectancy (years)"},
    )

    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True)
    )

    return fig


def _rank_bucket(series: pd.Series) -> pd.Series:
    """Assign observations to five roughly equal rank buckets."""
    percentile = series.rank(method="first", pct=True)

    return pd.cut(
        percentile,
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=BUCKETS,
        include_lowest=True,
    )


def build_sankey_data(
    classified_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Build 1960/2023 bucket assignments and the transition matrix."""
    endpoint = classified_df[
        classified_df["Year"].isin([1960, 2023])
        & classified_df["LifeExp_Total"].notna()
    ].copy()

    endpoint["Bucket"] = endpoint.groupby("Year")[
        "LifeExp_Total"
    ].transform(_rank_bucket)

    pivot = (
        endpoint.pivot_table(
            index=["Country Code", "Country Name"],
            columns="Year",
            values="Bucket",
            aggfunc="first",
        )
        .reset_index()
        .dropna(subset=[1960, 2023])
    )

    transition = pd.crosstab(
        pivot[1960], pivot[2023]
    ).reindex(
        index=BUCKETS,
        columns=BUCKETS,
        fill_value=0,
    )

    return pivot, transition


def plot_life_expectancy_sankey(
    classified_df: pd.DataFrame,
) -> Tuple[go.Figure, pd.DataFrame, pd.DataFrame]:
    """Create the required 1960-to-2023 Sankey diagram."""
    pivot, transition = build_sankey_data(classified_df)

    labels = (
        [f"1960 — {bucket}" for bucket in BUCKETS]
        + [f"2023 — {bucket}" for bucket in BUCKETS]
    )

    sources = []
    targets = []
    values = []

    for source_idx, source_bucket in enumerate(BUCKETS):
        for target_idx, target_bucket in enumerate(BUCKETS):
            value = int(transition.loc[source_bucket, target_bucket])

            if value > 0:
                sources.append(source_idx)
                targets.append(len(BUCKETS) + target_idx)
                values.append(value)

    fig = go.Figure(
        go.Sankey(
            node=dict(
                label=labels,
                pad=15,
                thickness=18,
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
            ),
        )
    )

    fig.update_layout(
        title="Life Expectancy Rank-Category Transitions: 1960 → 2023",
        font_size=12,
    )

    return fig, pivot, transition


def save_required_visualizations(
    classified_df: pd.DataFrame,
    output_dir: Path = VIS_DIR,
) -> None:
    """Save the three required visualizations as standalone HTML files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_life_expectancy_by_income_group(classified_df).write_html(
        output_dir / "01_life_expectancy_by_income_group.html"
    )

    plot_2023_world_map(classified_df).write_html(
        output_dir / "02_life_expectancy_world_map_2023.html"
    )

    plot_life_expectancy_sankey(classified_df)[0].write_html(
        output_dir / "03_life_expectancy_sankey.html"
    )


if __name__ == "__main__":
    data_path = PROJECT_DIR / "data" / "processed" / "classified_dataset.csv"

    if not data_path.exists():
        raise FileNotFoundError(
            "classified_dataset.csv not found. Run "
            "src/data_preprocessing.py first."
        )

    save_required_visualizations(pd.read_csv(data_path))
    print(f"Saved required visualizations to: {VIS_DIR}")
