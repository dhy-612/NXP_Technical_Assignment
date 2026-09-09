"""The pipeline performs:
1. Data preprocessing
2. Q1, Q2 and Q3 statistical analysis
3. Generation of the three required visualizations
"""

from src.data_preprocessing import build_datasets
from src.statistical_analysis import run_all_analyses
from src.visualizations import save_required_visualizations


def main() -> None:
    print("=" * 70)
    print("NXP DATA SCIENTIST ASSIGNMENT - ANALYSIS PIPELINE")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Data preprocessing
    # ------------------------------------------------------------------
    print("\n[1/3] Building processed datasets...")
    master_df, classified_df = build_datasets()

    print(f"Master dataset      : {master_df.shape[0]:,} rows x {master_df.shape[1]} columns")
    print(f"Classified dataset  : {classified_df.shape[0]:,} rows x {classified_df.shape[1]} columns")

    # ------------------------------------------------------------------
    # 2. Statistical analysis
    # ------------------------------------------------------------------
    print("\n[2/3] Running statistical analysis...")
    results = run_all_analyses(classified_df)

    print("\nQ1 - Gender-gap movement")
    print(results["q1_summary"].to_string(index=False))

    print("\nQ2 - Life-expectancy variability")
    print(results["q2_summary"].to_string(index=False))

    q3 = results["q3_result"]

    print("\nQ3 - Highest positive correlation")
    print(q3.nlargest(1, "Correlation").to_string(index=False))

    print("\nQ3 - Most negative correlation")
    print(q3.nsmallest(1, "Correlation").to_string(index=False))

    print("\nQ3 - Strongest absolute correlation")
    print(q3.nlargest(1, "Absolute_Correlation").to_string(index=False))

    # ------------------------------------------------------------------
    # 3. Required visualizations
    # ------------------------------------------------------------------
    print("\n[3/3] Generating required visualizations...")
    save_required_visualizations(classified_df)

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print("Processed data : data/processed/")
    print("Visualizations : visualizations/")


if __name__ == "__main__":
    main()
