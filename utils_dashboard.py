import polars as pl
import streamlit as st
from millify import millify


def scenario_sliders(scenario: str):
    st.subheader(f"Scenario {scenario}:")
    property_price = st.slider(
        label=f"Property price - {scenario}",
        min_value=1_000_000,
        max_value=20_000_000,
        value=5_500_000,
        step=500_000,
    )
    loan_amount = st.slider(
        label=f"Loan - {scenario}",
        min_value=0,
        max_value=10_000_000,
        value=2_500_000,
        step=500_000,
    )

    loan_term_years = st.slider(
        label=f"Loan remaining years - {scenario}", min_value=1, max_value=30, value=25
    )

    initial_stock_investment = st.slider(
        label=f"Initial stock investment - {scenario}",
        min_value=0,
        max_value=2_000_000,
        value=0,
        step=50_000,
    )
    monthly_stock_investment = st.slider(
        label=f"Monthly stock investment - {scenario}",
        min_value=0,
        max_value=50_000,
        value=15_000,
        step=1_000,
    )
    return (
        property_price,
        loan_amount,
        loan_term_years,
        initial_stock_investment,
        monthly_stock_investment,
    )


def stats_components(
    df_scenario: pl.DataFrame, monthly_stock_investment: float, scenario: str
):
    # initial_equity =
    # st.metric(
    #     label=f"Initial equity - {scenario}",
    #     value=millify(df_scenario["loan_payment"][1], precision=1),
    # )
    st.metric(
        label=f"Monthly loan payment - {scenario}",
        value=millify(df_scenario["loan_payment"][1], precision=1),
    )
    st.metric(
        label=f"Real loan cost - {scenario}",
        value=millify(df_scenario["net_cost"][1], precision=1),
        help="{scenario}fter tax deduction",
    )
    st.metric(
        label=f"Monthly payment - {scenario}",
        value=millify(
            monthly_stock_investment + df_scenario["loan_payment"][1],
            precision=1,
        ),
    )
    st.metric(
        label=f"Real monthly payment - {scenario}",
        value=millify(
            monthly_stock_investment + df_scenario["net_cost"][1],
            precision=1,
        ),
    )
