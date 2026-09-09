# ============================================================
# NXP DATA SCIENTIST TECHNICAL ASSIGNMENT
# GLOBAL LIFE EXPECTANCY DASHBOARD
# ============================================================

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Global Life Expectancy Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. PROJECT PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent

PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

# The dashboard uses the classified dataset because the
# assignment asks for country, region and income-group analysis.
DATA_PATH = PROCESSED_DIR / "classified_dataset.csv"


# ============================================================
# 3. CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.4rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            color: #666666;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 4. LOAD DATA
# ============================================================

@st.cache_data
def load_data(path: Path) -> pd.DataFrame:

    if not path.exists():
        raise FileNotFoundError(
            f"Processed dataset not found:\n{path}"
        )

    df = pd.read_csv(path)

    numeric_columns = [
        "Year",
        "LifeExp_Total",
        "LifeExp_Male",
        "LifeExp_Female",
        "Death_Rate",
        "Fertility_Rate",
        "Gender_Gap",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    df = df[
        df["Year"].between(1960, 2023)
    ].copy()

    return df


try:
    df = load_data(DATA_PATH)

except Exception as error:
    st.error(
        "Unable to load the dashboard dataset."
    )
    st.code(str(error))
    st.stop()


# ============================================================
# 5. HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🌍 Global Life Expectancy Dashboard'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Life expectancy, mortality, fertility and gender differences '
    'across countries from 1960 to 2023.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# 6. SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Filters")


# ------------------------------------------------------------
# Income Group
# ------------------------------------------------------------

income_groups = sorted(
    df["IncomeGroup"]
    .dropna()
    .unique()
    .tolist()
)

selected_income_group = st.sidebar.selectbox(
    "Income Group",
    options=["All"] + income_groups,
)


# ------------------------------------------------------------
# Region
# ------------------------------------------------------------

region_source = df.copy()

if selected_income_group != "All":
    region_source = region_source[
        region_source["IncomeGroup"]
        == selected_income_group
    ]

regions = sorted(
    region_source["Region"]
    .dropna()
    .unique()
    .tolist()
)

selected_region = st.sidebar.selectbox(
    "Region",
    options=["All"] + regions,
)


# ------------------------------------------------------------
# Country
# ------------------------------------------------------------

country_source = region_source.copy()

if selected_region != "All":
    country_source = country_source[
        country_source["Region"]
        == selected_region
    ]

countries = sorted(
    country_source["Country Name"]
    .dropna()
    .unique()
    .tolist()
)

selected_country = st.sidebar.selectbox(
    "Country",
    options=["All"] + countries,
)


# ------------------------------------------------------------
# Year range
# ------------------------------------------------------------

selected_years = st.sidebar.slider(
    "Year Range",
    min_value=1960,
    max_value=2023,
    value=(1960, 2023),
    step=1,
)


# ============================================================
# 7. APPLY FILTERS
# ============================================================

filtered_df = df.copy()

if selected_income_group != "All":
    filtered_df = filtered_df[
        filtered_df["IncomeGroup"]
        == selected_income_group
    ]

if selected_region != "All":
    filtered_df = filtered_df[
        filtered_df["Region"]
        == selected_region
    ]

if selected_country != "All":
    filtered_df = filtered_df[
        filtered_df["Country Name"]
        == selected_country
    ]

filtered_df = filtered_df[
    filtered_df["Year"].between(
        selected_years[0],
        selected_years[1],
    )
].copy()


# ============================================================
# 8. EMPTY FILTER RESULT
# ============================================================

if filtered_df.empty:
    st.warning(
        "No data is available for the selected filters."
    )
    st.stop()


# ============================================================
# 9. FILTER SUMMARY
# ============================================================

number_of_countries = filtered_df[
    "Country Code"
].nunique()

number_of_years = filtered_df[
    "Year"
].nunique()

latest_year = int(
    filtered_df["Year"].max()
)

st.info(
    f"Showing {number_of_countries} country(s) "
    f"across {number_of_years} year(s), "
    f"ending in {latest_year}."
)


# ============================================================
# 10. LATEST-YEAR DATA FOR KPI CARDS
# ============================================================

latest_data = filtered_df[
    filtered_df["Year"] == latest_year
].copy()


def mean_or_none(series):
    values = series.dropna()

    if values.empty:
        return None

    return values.mean()


life_expectancy = mean_or_none(
    latest_data["LifeExp_Total"]
)

male_life_expectancy = mean_or_none(
    latest_data["LifeExp_Male"]
)

female_life_expectancy = mean_or_none(
    latest_data["LifeExp_Female"]
)

gender_gap = mean_or_none(
    latest_data["Gender_Gap"]
)

death_rate = mean_or_none(
    latest_data["Death_Rate"]
)

fertility_rate = mean_or_none(
    latest_data["Fertility_Rate"]
)


# ============================================================
# 11. KPI CARDS
# ============================================================

st.subheader("Key Indicators")

kpi_1, kpi_2, kpi_3 = st.columns(3)
kpi_4, kpi_5, kpi_6 = st.columns(3)


with kpi_1:
    st.metric(
        f"Life Expectancy ({latest_year})",
        (
            f"{life_expectancy:.2f} years"
            if life_expectancy is not None
            else "N/A"
        ),
    )

with kpi_2:
    st.metric(
        f"Male Life Expectancy ({latest_year})",
        (
            f"{male_life_expectancy:.2f} years"
            if male_life_expectancy is not None
            else "N/A"
        ),
    )

with kpi_3:
    st.metric(
        f"Female Life Expectancy ({latest_year})",
        (
            f"{female_life_expectancy:.2f} years"
            if female_life_expectancy is not None
            else "N/A"
        ),
    )

with kpi_4:
    st.metric(
        f"Gender Gap ({latest_year})",
        (
            f"{gender_gap:.2f} years"
            if gender_gap is not None
            else "N/A"
        ),
    )

with kpi_5:
    st.metric(
        f"Death Rate ({latest_year})",
        (
            f"{death_rate:.2f}"
            if death_rate is not None
            else "N/A"
        ),
    )

with kpi_6:
    st.metric(
        f"Fertility Rate ({latest_year})",
        (
            f"{fertility_rate:.2f}"
            if fertility_rate is not None
            else "N/A"
        ),
    )


# ============================================================
# 12. LIFE EXPECTANCY TREND
# ============================================================

st.subheader("Life Expectancy Trend")

if selected_country != "All":

    life_trend = (
        filtered_df
        .groupby("Year", as_index=False)
        .agg(
            LifeExp_Total=(
                "LifeExp_Total",
                "mean",
            )
        )
    )

    life_title = (
        f"Life Expectancy Trend — "
        f"{selected_country}"
    )

else:

    life_trend = (
        filtered_df
        .groupby("Year", as_index=False)
        .agg(
            LifeExp_Total=(
                "LifeExp_Total",
                "mean",
            )
        )
    )

    life_title = (
        "Average Life Expectancy Trend"
    )


fig_life = px.line(
    life_trend,
    x="Year",
    y="LifeExp_Total",
    markers=True,
    title=life_title,
    labels={
        "Year": "Year",
        "LifeExp_Total":
            "Life Expectancy (years)",
    },
)

fig_life.update_layout(
    height=450,
    hovermode="x unified",
)

st.plotly_chart(
    fig_life,
    use_container_width=True,
)


# ============================================================
# 13. MALE VS FEMALE LIFE EXPECTANCY
# ============================================================

st.subheader("Male vs Female Life Expectancy")

gender_trend = (
    filtered_df
    .groupby("Year", as_index=False)
    .agg(
        Male=(
            "LifeExp_Male",
            "mean",
        ),
        Female=(
            "LifeExp_Female",
            "mean",
        ),
    )
)

gender_long = gender_trend.melt(
    id_vars="Year",
    value_vars=["Male", "Female"],
    var_name="Sex",
    value_name="Life_Expectancy",
)

fig_gender = px.line(
    gender_long,
    x="Year",
    y="Life_Expectancy",
    color="Sex",
    markers=True,
    title="Male vs Female Life Expectancy",
    labels={
        "Year": "Year",
        "Life_Expectancy":
            "Life Expectancy (years)",
    },
)

fig_gender.update_layout(
    height=450,
    hovermode="x unified",
)

st.plotly_chart(
    fig_gender,
    use_container_width=True,
)


# ============================================================
# 14. GENDER GAP TREND
# ============================================================

st.subheader("Male-Female Life Expectancy Gap")

gap_trend = (
    filtered_df
    .groupby("Year", as_index=False)
    .agg(
        Gender_Gap=(
            "Gender_Gap",
            "mean",
        )
    )
)

fig_gap = px.line(
    gap_trend,
    x="Year",
    y="Gender_Gap",
    markers=True,
    title="Female − Male Life Expectancy",
    labels={
        "Year": "Year",
        "Gender_Gap":
            "Gender Gap (years)",
    },
)

fig_gap.add_hline(
    y=0,
    line_dash="dash",
)

fig_gap.update_layout(
    height=400,
    hovermode="x unified",
)

st.plotly_chart(
    fig_gap,
    use_container_width=True,
)


# ============================================================
# 15. DEATH RATE + FERTILITY RATE
# ============================================================

st.subheader("Death Rate and Fertility Rate")

rates_trend = (
    filtered_df
    .groupby("Year", as_index=False)
    .agg(
        Death_Rate=(
            "Death_Rate",
            "mean",
        ),
        Fertility_Rate=(
            "Fertility_Rate",
            "mean",
        ),
    )
)

death_col, fertility_col = st.columns(2)


with death_col:

    fig_death = px.line(
        rates_trend,
        x="Year",
        y="Death_Rate",
        markers=True,
        title="Death Rate",
        labels={
            "Year": "Year",
            "Death_Rate":
                "Deaths per 1,000 people",
        },
    )

    fig_death.update_layout(
        height=400,
        hovermode="x unified",
    )

    st.plotly_chart(
        fig_death,
        use_container_width=True,
    )


with fertility_col:

    fig_fertility = px.line(
        rates_trend,
        x="Year",
        y="Fertility_Rate",
        markers=True,
        title="Fertility Rate",
        labels={
            "Year": "Year",
            "Fertility_Rate":
                "Births per woman",
        },
    )

    fig_fertility.update_layout(
        height=400,
        hovermode="x unified",
    )

    st.plotly_chart(
        fig_fertility,
        use_container_width=True,
    )


# ============================================================
# 16. INCOME GROUP COMPARISON
# ============================================================

st.subheader("Income Group Comparison")

income_data = (
    df[
        df["Year"].between(
            selected_years[0],
            selected_years[1],
        )
    ]
    .groupby(
        ["Year", "IncomeGroup"],
        as_index=False,
    )
    .agg(
        Avg_Life_Expectancy=(
            "LifeExp_Total",
            "mean",
        )
    )
)

fig_income = px.line(
    income_data,
    x="Year",
    y="Avg_Life_Expectancy",
    color="IncomeGroup",
    title=(
        "Average Life Expectancy by Income Group"
    ),
    labels={
        "Year": "Year",
        "Avg_Life_Expectancy":
            "Life Expectancy (years)",
    },
)

fig_income.update_layout(
    height=450,
    hovermode="x unified",
)

st.plotly_chart(
    fig_income,
    use_container_width=True,
)


# ============================================================
# 17. REGION COMPARISON
# ============================================================

st.subheader("Regional Comparison")

region_data = (
    df[
        df["Year"].between(
            selected_years[0],
            selected_years[1],
        )
    ]
    .groupby(
        ["Year", "Region"],
        as_index=False,
    )
    .agg(
        Avg_Life_Expectancy=(
            "LifeExp_Total",
            "mean",
        )
    )
)

fig_region = px.line(
    region_data,
    x="Year",
    y="Avg_Life_Expectancy",
    color="Region",
    title=(
        "Average Life Expectancy by Region"
    ),
    labels={
        "Year": "Year",
        "Avg_Life_Expectancy":
            "Life Expectancy (years)",
    },
)

fig_region.update_layout(
    height=500,
    hovermode="x unified",
)

st.plotly_chart(
    fig_region,
    use_container_width=True,
)


# ============================================================
# 18. FILTERED DATA TABLE
# ============================================================

st.subheader("Filtered Data")

display_columns = [
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

display_df = (
    filtered_df[display_columns]
    .sort_values(
        ["Country Name", "Year"]
    )
    .reset_index(drop=True)
)

st.dataframe(
    display_df,
    width=1400,
    height=450,
    hide_index=True,
)


# ============================================================
# 19. FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Source: World Bank | "
    "Period: 1960–2023 | "
    "Python • Pandas • Plotly • Streamlit"
)
