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
    monthly_other_property_costs = st.slider(
        label=f"Monthly other property costs - {scenario}",
        min_value=0,
        max_value=20_000,
        value=6_000,
        step=1_000,
    )
    return (
        property_price,
        loan_amount,
        loan_term_years,
        initial_stock_investment,
        monthly_stock_investment,
        monthly_other_property_costs,
    )


def stats_components(
    df_scenario: pl.DataFrame,
    monthly_stock_investment: float,
    monthly_other_property_costs: float,
    scenario: str,
    property_price: float,
    loan_amount: float,
    initial_stock_investment: float,
):
    initial_equity = property_price - loan_amount + initial_stock_investment

    st.metric(
        label=f"Initial equity - {scenario}",
        value=millify(initial_equity, precision=2),
    )
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Monthly costs")
        st.metric(
            label=f"Monthly loan payment - {scenario}",
            value=millify(df_scenario["loan_payment"][1], precision=1),
        )
        st.metric(
            label=f"Monthly payment - {scenario}",
            value=millify(
                monthly_stock_investment
                + df_scenario["loan_payment"][1]
                + monthly_other_property_costs,
                precision=1,
            ),
            help="Stock investment + loan payment + other property costs",
        )

    with col2:
        st.subheader("Costs after tax deduction")
        st.metric(
            label=f"Real loan cost - {scenario}",
            value=millify(df_scenario["net_cost"][1], precision=1),
            help="After tax deduction",
        )
        st.metric(
            label=f"Real monthly payment - {scenario}",
            value=millify(
                monthly_stock_investment
                + df_scenario["net_cost"][1]
                + monthly_other_property_costs,
                precision=1,
            ),
            help="Stock investment + loan payment after tax deduction + other property costs",
        )


def scenario_end_stats(
    df_scenario: pl.DataFrame,
    scenario: str,
):
    with st.container(border=True):
        row = st.container(horizontal=True, horizontal_alignment="center")
        with row:
            st.metric(
                label=f"Total net worth - {scenario}",
                value=millify(df_scenario["total_net_worth"][-1], precision=2),
            )
            st.metric(
                label=f"Stock equity - {scenario}",
                value=millify(df_scenario["stock_equity"][-1], precision=2),
            )
            st.metric(
                label=f"House Equity - {scenario}",
                value=millify(df_scenario["property_equity"][-1], precision=2),
            )
            st.metric(
                label=f"Property value - {scenario}",
                value=millify(df_scenario["property_value"][-1], precision=2),
                width="content",
            )
