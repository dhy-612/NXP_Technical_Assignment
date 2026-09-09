"""Q1-Q3 statistical analysis for the NXP assignment."""

from pathlib import Path
from typing import Tuple

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"


def load_classified_dataset(
    path: Path = PROCESSED_DIR / "classified_dataset.csv",
) -> pd.DataFrame:
    """Load the analysis-ready classified dataset."""
    df = pd.read_csv(path)

    required_columns = {
        "Country Name",
        "Country Code",
        "IncomeGroup",
        "Year",
        "LifeExp_Total",
        "LifeExp_Male",
        "LifeExp_Female",
        "Fertility_Rate",
    }

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(
            f"Dataset is missing required columns: {sorted(missing)}"
        )

    return df


def q1_gender_gap_change(
    classified_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Measure cumulative year-to-year movement in the income-group gender gap."""
    work = classified_df.dropna(
        subset=["LifeExp_Male", "LifeExp_Female"]
    ).copy()

    work["Gender_Gap"] = (
        work["LifeExp_Female"] - work["LifeExp_Male"]
    )

    annual = (
        work.groupby(["IncomeGroup", "Year"], as_index=False)
        .agg(
            Avg_Male_Life_Expectancy=("LifeExp_Male", "mean"),
            Avg_Female_Life_Expectancy=("LifeExp_Female", "mean"),
            Gender_Gap=("Gender_Gap", "mean"),
        )
        .sort_values(["IncomeGroup", "Year"])
        .reset_index(drop=True)
    )

    annual["Gap_Yearly_Change"] = annual.groupby(
        "IncomeGroup"
    )["Gender_Gap"].diff()

    annual["Absolute_Gap_Change"] = annual["Gap_Yearly_Change"].abs()

    summary = (
        annual.groupby("IncomeGroup", as_index=False)
        .agg(
            Total_Absolute_Gap_Change=(
                "Absolute_Gap_Change",
                "sum",
            ),
            Gap_1960=("Gender_Gap", "first"),
            Gap_2023=("Gender_Gap", "last"),
        )
        .sort_values(
            "Total_Absolute_Gap_Change",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    summary["Endpoint_Gap_Change"] = (
        summary["Gap_2023"] - summary["Gap_1960"]
    )

    return summary, annual


def q2_life_expectancy_variability(
    classified_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Measure variance of annual income-group average life expectancy."""
    annual = (
        classified_df.dropna(subset=["LifeExp_Total"])
        .groupby(["IncomeGroup", "Year"], as_index=False)
        .agg(Avg_Life_Expectancy=("LifeExp_Total", "mean"))
        .sort_values(["IncomeGroup", "Year"])
        .reset_index(drop=True)
    )

    summary = (
        annual.groupby("IncomeGroup", as_index=False)
        .agg(
            Variance=("Avg_Life_Expectancy", "var"),
            Standard_Deviation=("Avg_Life_Expectancy", "std"),
            Mean_Life_Expectancy=("Avg_Life_Expectancy", "mean"),
            Min_Annual_Average=("Avg_Life_Expectancy", "min"),
            Max_Annual_Average=("Avg_Life_Expectancy", "max"),
        )
        .sort_values("Variance", ascending=False)
        .reset_index(drop=True)
    )

    summary["Range"] = (
        summary["Max_Annual_Average"]
        - summary["Min_Annual_Average"]
    )

    return summary, annual


def q3_fertility_life_expectancy_correlation(
    classified_df: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate Pearson correlation by entity using all paired observations."""
    records = []

    for (country_code, country_name), group in classified_df.groupby(
        ["Country Code", "Country Name"]
    ):
        paired = group[["LifeExp_Total", "Fertility_Rate"]].dropna()

        if len(paired) < 2:
            correlation = float("nan")
        else:
            correlation = paired["LifeExp_Total"].corr(
                paired["Fertility_Rate"],
                method="pearson",
            )

        records.append(
            {
                "Country Code": country_code,
                "Country Name": country_name,
                "Correlation": correlation,
                "Paired_Years": len(paired),
            }
        )

    result = pd.DataFrame(records).dropna(
        subset=["Correlation"]
    )

    result["Absolute_Correlation"] = result["Correlation"].abs()

    return result.sort_values(
        "Correlation", ascending=False
    ).reset_index(drop=True)


def run_all_analyses(classified_df: pd.DataFrame) -> dict:
    """Run Q1, Q2 and Q3 and return their outputs."""
    q1_summary, q1_annual = q1_gender_gap_change(classified_df)
    q2_summary, q2_annual = q2_life_expectancy_variability(classified_df)
    q3_result = q3_fertility_life_expectancy_correlation(classified_df)

    return {
        "q1_summary": q1_summary,
        "q1_annual": q1_annual,
        "q2_summary": q2_summary,
        "q2_annual": q2_annual,
        "q3_result": q3_result,
    }


if __name__ == "__main__":
    df = load_classified_dataset()
    results = run_all_analyses(df)

    print("\nQ1 - Gender-gap movement")
    print(results["q1_summary"].to_string(index=False))

    print("\nQ2 - Life-expectancy variability")
    print(results["q2_summary"].to_string(index=False))

    print("\nQ3 - Highest positive correlations")
    print(
        results["q3_result"]
        .nlargest(5, "Correlation")
        .to_string(index=False)
    )

    print("\nQ3 - Most negative correlations")
    print(
        results["q3_result"]
        .nsmallest(5, "Correlation")
        .to_string(index=False)
    )
