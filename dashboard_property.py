# uv run streamlit run dashboard_property.py --server.headless true

import plotly.express as px
import polars as pl
import streamlit as st
from millify import millify

from utils import property_equity_over_time


def main():
    st.set_page_config(
        page_title="Property & Mortgage Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # --- Sidebar inputs ---
    st.sidebar.header("Property Parameters")
    initial_price = st.sidebar.slider(
        label="Property price",
        min_value=2_000_000,
        max_value=20_000_000,
        value=8_000_000,
        step=500_000,
    )
    annual_value_change = st.sidebar.slider(
        label="Annual property value change (%)",
        min_value=-10.0,
        max_value=20.0,
        value=3.0,
        step=0.1,
    )
    loan_amount = st.sidebar.slider(
        label="Loan amount",
        min_value=0,
        max_value=20_000_000,
        value=5_000_000,
        step=500_000,
    )
    annual_interest_rate = st.sidebar.slider(
        label="Annual mortgage interest rate (%)",
        min_value=0.0,
        max_value=15.0,
        value=5.0,
        step=0.05,
    )
    loan_term_years = st.sidebar.slider(
        label="Loan term (years)", min_value=1, max_value=50, value=25
    )
    annual_inflation = st.sidebar.slider(
        label="Annual inflation (%)",
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.05,
    )
    years = st.sidebar.slider(
        label="Projection horizon (years)", min_value=1, max_value=50, value=25
    )
    rentefradrag = st.sidebar.checkbox(
        label="Include rentefradrag (22% tax deduction on interest)",
        value=True,
        help="The mortgage interest rate is adjusted to account for the tax deduction",
    )

    # --- Calculate projection ---
    df = property_equity_over_time(
        initial_price,
        annual_value_change / 100,  # convert % to decimal
        loan_amount,
        annual_interest_rate / 100,  # convert % to decimal
        loan_term_years,
        years,
        annual_inflation / 100,  # convert % to decimal
        rentefradrag=rentefradrag,
    )

    # --- Show stats ---
    if rentefradrag:
        annual_interest_rate = annual_interest_rate * (1 - 0.22)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Effective interest rate", f"{annual_interest_rate:.2f}")

    with col2:
        st.metric("Equity (end)", millify(df["equity"][-1], precision=1))

    with col3:
        st.metric(
            "property value (end)", millify(df["property_value"][-1], precision=1)
        )

    with col4:
        st.metric(
            "Total interest (end)", millify(df["cumulative_interest"][-1], precision=1)
        )

    with col5:
        st.metric(
            "Remaining loan (end)", millify(df["remaining_balance"][-1], precision=1)
        )

    # --- Plot over time ---
    st.subheader("Property & Mortgage Projection")

    fig = px.line(
        df.to_pandas(),
        x="month",
        y=["property_value", "remaining_balance", "equity"],
        labels={"value": "Amount", "month": "Month"},
        title="Property & Mortgage Projection",
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Show table ---
    st.subheader("Yearly Projection")
    df_yearly = df.filter(pl.col("month") % 12 == 0)
    st.dataframe(df_yearly, width=1800)


if __name__ == "__main__":
    main()
