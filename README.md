# NXP Data Scientist Technical Assignment

## Overview

This repository contains the solution for the NXP Data Scientist technical assignment using World Bank data related to life expectancy, mortality, and fertility.

The project includes:

- Data preprocessing
- Statistical analysis
- Three required visualizations
- An interactive Streamlit dashboard
- Reusable Python modules
- A single `main.py` entry point for the complete analysis pipeline

The analysis covers annual data from **1960 to 2023**.

Unless gender is explicitly specified, **total life expectancy at birth** is used as the primary life-expectancy measure.

---

## Dataset

The analysis uses the five indicators specified in the assignment:

| Indicator | World Bank Code | Project Column |
|---|---|---|
| Life expectancy at birth, total | `SP.DYN.LE00.IN` | `LifeExp_Total` |
| Life expectancy at birth, male | `SP.DYN.LE00.MA.IN` | `LifeExp_Male` |
| Life expectancy at birth, female | `SP.DYN.LE00.FE.IN` | `LifeExp_Female` |
| Death rate, crude | `SP.DYN.CDRT.IN` | `Death_Rate` |
| Fertility rate, total | `SP.DYN.TFRT.IN` | `Fertility_Rate` |

The original World Bank files contain data beyond 2023, but only **1960–2023** is used for this assignment.

---

# Project Structure

```text
NXP_Technical_Assignment/
│
├── README.md
├── requirements.txt
├── main.py
├── app.py
│
├── data/
│   ├── raw/
│   │   ├── API_SP.DYN.CDRT.IN_DS2_en_csv_v2_33278/
│   │   ├── API_SP.DYN.LE00.FE.IN_DS2_en_csv_v2_34008/
│   │   ├── API_SP.DYN.LE00.IN_DS2_en_csv_v2_408/
│   │   ├── API_SP.DYN.LE00.MA.IN_DS2_en_csv_v2_189/
│   │   └── API_SP.DYN.TFRT.IN_DS2_EN_csv_v2_33381/
│   │
│   └── processed/
│       ├── master_dataset.csv
│       └── classified_dataset.csv
│
├── notebooks/
│   └── analysis.ipynb
│
├── src/
│   ├── __init__.py
│   ├── data_preprocessing.py
│   ├── statistical_analysis.py
│   └── visualizations.py
│
└── visualizations/
    ├── 01_life_expectancy_by_income_group.html
    ├── 02_life_expectancy_world_map_2023.html
    └── 03_life_expectancy_sankey.html
```

---

# 1. Data Preparation

## Preprocessing Workflow

The preprocessing pipeline:

1. Reads the five World Bank indicator CSV files.
2. Skips the metadata/header rows in the downloaded files.
3. Keeps observations from **1960 to 2023**.
4. Converts the datasets from wide format into long format.
5. Converts indicator values to numeric values.
6. Loads country metadata containing `Region` and `IncomeGroup`.
7. Merges all indicators using `Country Code + Year`.
8. Creates the female-minus-male life expectancy gap:

```text
Gender_Gap = LifeExp_Female - LifeExp_Male
```

9. Validates the uniqueness of `Country Code + Year`.
10. Saves the cleaned datasets under `data/processed/`.

`Country Code + Year` is used as the merge key rather than country name because country names can vary between indicator files.

---

## Master Dataset

`master_dataset.csv` is the complete cleaned dataset produced from the five indicator files.

It contains:

- **265 source entities**
- **64 years**
- **16,960 rows** (`265 × 64`)
- Classified entities plus aggregate/unclassified entities

The master dataset is the complete cleaned source-of-truth after preprocessing.

---

## Classified Dataset

`classified_dataset.csv` is derived from the master dataset by retaining only observations with a non-null `IncomeGroup`.

```python
classified_df = master_df[master_df["IncomeGroup"].notna()].copy()
```

It contains:

- **217 classified entities**
- **64 years**
- **13,888 rows** (`217 × 64`)

Income-group distribution:

| Income Group | Entities |
|---|---:|
| High income | 86 |
| Upper middle income | 59 |
| Lower middle income | 47 |
| Low income | 25 |

The classified dataset is used for:

- Income-group statistical analysis
- Country-level correlation analysis
- Country-level visualizations
- Dashboard analysis

Aggregate/unclassified entities are excluded from these analyses because they do not have an income-group classification.

---

# 2. Statistical Analysis

## Q1. Which income group has the largest change in the average male-female life expectancy difference?

All years from **1960 to 2023** are used.

For every year and income group:

```text
Gender Gap = Average Female Life Expectancy - Average Male Life Expectancy
```

The annual change is:

```text
Yearly Change = Current Year Gap - Previous Year Gap
```

To measure movement over the complete time series, the ranking metric is:

```text
Total Absolute Gap Change = Σ |Yearly Change|
```

This measures cumulative year-to-year movement rather than only comparing 1960 and 2023.

### Result

| Rank | Income Group | Total Absolute Gap Change |
|---:|---|---:|
| 1 | Low income | **8.797** |
| 2 | Lower middle income | 7.539 |
| 3 | Upper middle income | 5.214 |
| 4 | High income | 4.240 |

### Finding

**Low income** has the largest cumulative movement in the average male-female life expectancy gap.

For the low-income group:

- 1960 gender gap: **2.840 years**
- 2023 gender gap: **4.399 years**
- Endpoint change: **+1.559 years**
- Cumulative absolute year-to-year movement: **8.797 years**

The value 8.797 represents cumulative movement across the annual changes. It is not an 8.797-year increase in the gender gap.

---

## Q2. Which income group has the greatest variability in life expectancy at birth?

For every year from **1960 to 2023**, the average total life expectancy is calculated for each income group.

Variability is measured using the variance of those **64 annual income-group average life-expectancy values**.

### Result

| Rank | Income Group | Variance | Standard Deviation |
|---:|---|---:|---:|
| 1 | Low income | **51.517** | 7.178 |
| 2 | Lower middle income | 42.370 | 6.509 |
| 3 | Upper middle income | 29.605 | 5.441 |
| 4 | High income | 19.060 | 4.366 |

### Finding

**Low income** has the greatest variability in life expectancy over the 1960–2023 period.

For the low-income group:

- Mean annual average life expectancy: **50.425 years**
- Minimum annual average: **39.761 years**
- Maximum annual average: **64.202 years**
- Range: **24.441 years**

The assignment does not define a specific mathematical formula for “variability”; therefore, this project explicitly defines it as the variance of annual income-group average life expectancy across the full period.

---

## Q3. Which countries have the highest correlation between fertility rate and life expectancy?

For every classified entity, Pearson correlation is calculated between:

- `LifeExp_Total`
- `Fertility_Rate`

All available paired observations from **1960–2023** are used for each entity.

### Results

**Highest positive correlation**

```text
Zimbabwe: +0.345
```

**Most negative correlation**

```text
India: -0.997
```

**Strongest absolute correlation**

```text
India: -0.997
```

Correlation measures association and does not by itself establish causation.

---

# 3. Required Visualizations

## Visualization 1 — Life Expectancy by Income Group

A time-series line chart showing average total life expectancy for each income group from 1960 to 2023.

Output:

```text
visualizations/01_life_expectancy_by_income_group.html
```

---

## Visualization 2 — World Map of Life Expectancy in 2023

A Plotly choropleth map showing country-level total life expectancy in 2023.

Aggregate/unclassified entities are excluded by using the classified dataset.

Output:

```text
visualizations/02_life_expectancy_world_map_2023.html
```

---

## Visualization 3 — Life Expectancy Rank-Category Sankey

Countries are ranked separately in 1960 and 2023 according to total life expectancy and divided into five roughly equal categories:

1. Very low
2. Low
3. Medium
4. High
5. Very high

The Sankey diagram shows transitions between these categories from 1960 to 2023.

There are **217 classified entities**.

### 1960 bucket sizes

```text
Very low   = 43
Low        = 43
Medium     = 43
High       = 43
Very high  = 43
```

### 2023 bucket sizes

```text
Very low   = 43
Low        = 43
Medium     = 44
High       = 43
Very high  = 44
```

Output:

```text
visualizations/03_life_expectancy_sankey.html
```

---

# 4. Interactive Dashboard

`app.py` provides an interactive Streamlit dashboard for monitoring life expectancy, death rate, and fertility rate.

The dashboard includes:

- Total life expectancy
- Male life expectancy
- Female life expectancy
- Female-minus-male life expectancy gap
- Death rate
- Fertility rate
- Income group
- Region
- Historical trends

## Filters

The dashboard supports:

- Country
- Income group
- Region
- Year range

## Additional Comparisons

The dashboard also provides comparison views by:

- Income group
- Region

Run the dashboard with:

```bash
python -m streamlit run app.py
```

---

# 5. Reusable Source Code

## `src/data_preprocessing.py`

Handles:

- Reading raw World Bank files
- Wide-to-long transformation
- Country metadata loading
- Indicator merging
- Gender-gap creation
- Master dataset creation
- Classified dataset creation

## `src/statistical_analysis.py`

Contains functions for:

- Q1 — Gender-gap movement
- Q2 — Life-expectancy variability
- Q3 — Fertility/life-expectancy correlation

## `src/visualizations.py`

Contains functions for:

- Income-group life expectancy trend
- 2023 world map
- 1960 → 2023 Sankey diagram

---

# 6. Main Entry Point

`main.py` is the single entry point for the complete analysis pipeline.

It executes the workflow in this order:

```text
main.py
   │
   ├── Data preprocessing
   │       ↓
   │   master_dataset.csv
   │   classified_dataset.csv
   │
   ├── Statistical analysis
   │       ↓
   │   Q1, Q2, Q3
   │
   └── Visualization generation
           ↓
       Three required HTML visualizations
```

Run the complete pipeline with:

```bash
python main.py
```

This makes it possible to reproduce the main analysis without manually running each source file.

---

# 7. Notebook

`notebooks/analysis.ipynb` contains the complete analysis workflow in a readable, report-style format.

It includes:

- Dataset inspection
- Data preprocessing
- Validation
- Master vs classified dataset explanation
- Q1 analysis
- Q2 analysis
- Q3 analysis
- Required visualizations
- Final findings

The notebook uses project-relative paths and is intended to run from the repository.

---

# 8. Installation

A project-local virtual environment is recommended.

### Create virtual environment

Windows:

```bash
py -3.9 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

---

# 9. Running the Project

From the repository root:

### Complete analysis pipeline

```bash
python main.py
```

This runs:

```text
Preprocessing
→ Statistical Analysis
→ Visualization Generation
```

### Dashboard

```bash
python -m streamlit run app.py
```

### Notebook

Open:

```text
notebooks/analysis.ipynb
```

and execute the cells sequentially.

---

# 10. Reproducibility

The project is designed to reproduce the analysis from the provided World Bank datasets.

The workflow uses:

- Explicit indicator-to-folder mapping
- Explicit year range: 1960–2023
- Relative project paths
- `Country Code + Year` as the merge key
- Merge validation
- Numeric conversion with missing values handled as `NaN`
- Reusable functions under `src/`

The local Python virtual environment should not be uploaded to GitHub.

---

# 11. Technology Stack

- Python
- Pandas
- NumPy
- Plotly
- Streamlit
- Jupyter Notebook

---

# 12. Data Source

**World Bank — World Development Indicators**

The five indicators used in this project are the indicators specified in the NXP assignment.

---

# 13. Key Findings

- **Low income** has the largest cumulative movement in the average male-female life expectancy gap.
- **Low income** has the greatest variance in annual average life expectancy across 1960–2023.
- **Zimbabwe** has the highest positive fertility/life-expectancy correlation.
- **India** has the most negative and strongest absolute correlation.

Overall, the analysis shows substantial long-term differences in life expectancy across income groups, with lower-income groups showing greater movement and variability over the historical period.
