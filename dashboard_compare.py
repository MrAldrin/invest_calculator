# uv run streamlit run dashboard_compare.py --server.headless true

import plotly.express as px
import polars as pl
import polars.selectors as cs
import streamlit as st
from millify import millify

from utils import (
    combined_property_and_stocks,
)


def main():
    st.set_page_config(
        page_title="Investment Comparison Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Investment Comparison calculator:")

    # Common Parameters
    st.sidebar.header("Shared Parameters")
    time_horizon_years = st.sidebar.slider(
        label="Projection horizon (years)", min_value=1, max_value=25, value=15
    )
    annual_inflation = st.sidebar.slider(
        label="Annual inflation (%)",
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.1,
    )
    annual_stock_return = st.sidebar.slider(
        label="Annual stock return (%)",
        min_value=0.0,
        max_value=20.0,
        value=10.0,
        step=0.5,
    )
    annual_property_appreciation = st.sidebar.slider(
        label="Annual house value change (%)",
        min_value=-10.0,
        max_value=10.0,
        value=5.0,
        step=0.1,
    )
    annual_interest_rate = st.sidebar.slider(
        label="Mortgage interest rate (%)",
        min_value=0.0,
        max_value=15.0,
        value=4.0,
        step=0.1,
    )
    rentefradrag = st.sidebar.checkbox(
        label="Include rentefradrag (22% tax deduction on interest)",
        value=True,
        help="The mortgage interest rate is adjusted to account for the tax deduction",
    )

    if rentefradrag:
        annual_interest_rate = annual_interest_rate * (1 - 0.22)
    st.sidebar.metric("Effective interest rate", f"{annual_interest_rate:.2f}%")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Scenario A:")
        property_price_1 = st.slider(
            label="Property price - A",
            min_value=1_000_000,
            max_value=20_000_000,
            value=5_500_000,
            step=500_000,
        )
        loan_amount_1 = st.slider(
            label="Loan - A",
            min_value=0,
            max_value=10_000_000,
            value=2_500_000,
            step=500_000,
        )

        loan_term_years_1 = st.slider(
            label="Loan remaining years - A", min_value=1, max_value=30, value=25
        )

        initial_stock_investment_1 = st.slider(
            label="Initial stock investment - A",
            min_value=0,
            max_value=2_000_000,
            value=0,
            step=50_000,
        )
        monthly_stock_investment_1 = st.slider(
            label="Monthly stock investment - A",
            min_value=0,
            max_value=50_000,
            value=15_000,
            step=1_000,
        )

    # Alternative 2
    with col2:
        st.subheader("Scenario B:")
        property_price_2 = st.slider(
            label="Property price - B",
            min_value=1_000_000,
            max_value=20_000_000,
            value=9_500_000,
            step=500_000,
        )
        loan_amount_2 = st.slider(
            label="Loan - B",
            min_value=0,
            max_value=10_000_000,
            value=6_500_000,
            step=500_000,
        )

        loan_term_years_2 = st.slider(
            label="Loan remaining years - B", min_value=1, max_value=30, value=25
        )

        initial_stock_investment_2 = st.slider(
            label="Initial stock investment - B",
            min_value=0,
            max_value=2_000_000,
            value=0,
            step=50_000,
        )

        monthly_stock_investment_2 = st.slider(
            label="Monthly stock investment - B",
            min_value=0,
            max_value=50_000,
            value=0,
            step=1_000,
        )

    # --- Calculate projections ---

    # Scenario 1: Current house + stocks
    scenario1_df = combined_property_and_stocks(
        property_price=property_price_1,
        annual_property_appreciation=annual_property_appreciation / 100,
        loan_amount=loan_amount_1,
        annual_interest_rate=annual_interest_rate / 100,
        loan_term_years=loan_term_years_1,
        initial_stock_investment=initial_stock_investment_1,
        monthly_stock_investment=monthly_stock_investment_1,
        annual_stock_return=annual_stock_return / 100,
        time_horizon_years=time_horizon_years,
        annual_inflation=annual_inflation / 100,
        rentefradrag=rentefradrag,
    )

    # Scenario 2: Bigger house
    scenario2_df = combined_property_and_stocks(
        property_price=property_price_2,
        annual_property_appreciation=annual_property_appreciation / 100,
        loan_amount=loan_amount_2,
        annual_interest_rate=annual_interest_rate / 100,
        loan_term_years=loan_term_years_2,
        initial_stock_investment=initial_stock_investment_2,
        monthly_stock_investment=monthly_stock_investment_2,
        annual_stock_return=annual_stock_return / 100,
        time_horizon_years=time_horizon_years,
        annual_inflation=annual_inflation / 100,
        rentefradrag=rentefradrag,
    )
    # --- Show scenario stats ---
    with col1:
        st.metric(
            label="Monthly loan payment - A",
            value=millify(scenario1_df["loan_payment"][1], precision=3),
        )
        st.metric(
            label="Real loan cost - A",
            value=millify(scenario1_df["net_cost"][1], precision=3),
            help="After tax deduction",
        )
    with col2:
        st.metric(
            label="Monthly loan payment - B",
            value=millify(scenario2_df["loan_payment"][1], precision=3),
        )
        st.metric(
            label="Real loan cost - B",
            value=millify(scenario2_df["net_cost"][1], precision=3),
            help="After tax deduction",
        )

    # --- Show comparison stats ---
    st.subheader("Final Values Comparison")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Scenario A:",
            millify(scenario1_df["total_net_worth"][-1], precision=1),
        )
        st.caption("Scenario A")

    with col2:
        st.metric(
            "Scenario B:", millify(scenario2_df["property_equity"][-1], precision=1)
        )
        st.caption("Scenario B:")

    with col3:
        difference = (
            scenario1_df["total_net_worth"][-1] - scenario2_df["total_net_worth"][-1]
        )
        st.metric(
            "Difference (Scenario A - B)",
            millify(difference, precision=1),
            # delta=millify(difference, precision=1) if difference != 0 else "0",
        )

    # --- Plot comparison ---
    st.subheader("Net Worth Comparison Over Time")

    # Prepare data for plotting
    plot_df = pl.DataFrame(
        {
            "month": scenario1_df["month"],
            "scenario_A": scenario1_df["total_net_worth"],
            "scenario_B": scenario2_df["total_net_worth"],
        }
    ).with_columns((pl.col("scenario_A") - pl.col("scenario_B")).alias("scenario_diff"))

    fig = px.line(
        plot_df,
        x="month",
        y=["scenario_A", "scenario_B", "scenario_diff"],
        labels={"value": "Net Worth", "month": "Years"},
        title="Investment Scenarios Comparison",
    )
    max_month = plot_df["month"].max()
    year_ticks = list(range(0, max_month + 1, 12))
    fig.update_xaxes(
        tickmode="array",
        tickvals=year_ticks,
        ticktext=[str(y) for y in range(len(year_ticks))],
    )

    for trace in fig.data:
        if trace.name in ("scenario_A", "scenario_B"):
            trace.visible = "legendonly"
    st.plotly_chart(fig, use_container_width=True)

    # --- Detailed breakdown for Scenario 1 ---
    st.subheader("Scenario 1 Breakdown")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "House Equity (end)",
            millify(scenario1_df["property_equity"][-1], precision=1),
        )

    with col2:
        st.metric(
            "Stock Portfolio (end)",
            millify(scenario1_df["stock_balance"][-1], precision=1),
        )

    with col3:
        st.metric(
            "Stock Returns (end)",
            millify(scenario1_df["stock_returns"][-1], precision=1),
        )

    # --- Show detailed tables ---
    st.subheader("Yearly Projections")

    numeric_cols = scenario1_df.select(cs.numeric()).columns

    st.write("**Scenario A:**")
    scenario1_yearly = scenario1_df.filter(
        (pl.col("month") % 12 == 0) | (pl.col("month") == 1)
    )
    st.dataframe(
        scenario1_yearly,
        column_config={
            col: st.column_config.NumberColumn(format="%d") for col in numeric_cols
        },
    )

    st.write("**Scenario B:**")
    scenario2_yearly = scenario2_df.filter(
        (pl.col("month") % 12 == 0) | (pl.col("month") == 1)
    )
    st.dataframe(
        scenario2_yearly,
        column_config={
            col: st.column_config.NumberColumn(format="%d") for col in numeric_cols
        },
    )


if __name__ == "__main__":
    main()
