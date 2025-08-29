# uv run streamlit run dashboard_investment.py --server.headless true


import plotly.express as px
import polars as pl
import streamlit as st
from millify import millify

from utils import stock_investment_monthly


def main():
    st.set_page_config(
        page_title="Investment Dashboard",
        layout="wide",  # important! makes the main content use more horizontal space
        initial_sidebar_state="expanded",
    )
    # --- Sidebar inputs ---
    st.sidebar.header("Investment Parameters")
    initial_investment = st.sidebar.slider(
        label="Initial investment",
        min_value=0,
        max_value=500000,
        value=15000,
        step=5000,
    )
    monthly_contribution = st.sidebar.slider(
        label="Monthly contribution",
        min_value=0,
        max_value=40000,
        value=15000,
        step=500,
    )
    annual_return = st.sidebar.slider(
        label="Annual return (%)", min_value=0.0, max_value=20.0, value=7.0, step=0.05
    )
    annual_inflation = st.sidebar.slider(
        label="Annual inflation (%)",
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.05,
    )
    years = st.sidebar.slider(label="Years", min_value=1, max_value=50, value=20)

    # --- Calculate projection ---
    df = stock_investment_monthly(
        initial_investment,
        monthly_contribution,
        annual_return / 100,  # convert % to decimal
        years,
        annual_inflation / 100,  # convert % to decimal
    )

    # --- Show stats ---

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("balance (end)", millify(df["balance"][-1], precision=1))

    with col2:
        st.metric(
            "contributions_cum (end)", millify(df["contributions_cum"][-1], precision=1)
        )

    with col3:
        st.metric("returns_cum (end)", millify(df["returns_cum"][-1], precision=1))

    # --- Plot balance over time ---
    st.subheader("Portfolio Projection")

    # --- Plot in the left column ---

    fig = px.line(
        df.to_pandas(),
        x="month",
        y=["balance", "returns_cum", "contributions_cum"],
        labels={"value": "Amount", "month": "Month"},
        title="Portfolio Projection",
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Show table ---
    st.subheader("Yearly Projection")
    df_yearly = df.filter(pl.col("month") % 12 == 0)
    st.dataframe(df_yearly, width=1800)


if __name__ == "__main__":
    main()
