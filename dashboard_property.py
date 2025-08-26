# uv run streamlit run dashboard_property.py --server.headless true

import plotly.express as px
import polars as pl
import streamlit as st

from utils import house_equity_over_time


def main():
    st.set_page_config(
        page_title="House & Mortgage Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # --- Sidebar inputs ---
    st.sidebar.header("House Parameters")
    initial_price = st.sidebar.slider(
        label="House price",
        min_value=2_000_000,
        max_value=20_000_000,
        value=8_000_000,
        step=500_000,
    )
    annual_value_change = st.sidebar.slider(
        label="Annual house value change (%)",
        min_value=-10.0,
        max_value=20.0,
        value=3.0,
        step=0.1,
    )
    loan_amount = st.sidebar.slider(
        label="Loan amount",
        min_value=0,
        max_value=20_000_000,
        value=8_000_000,
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

    # --- Calculate projection ---
    df = house_equity_over_time(
        initial_price,
        annual_value_change / 100,  # convert % to decimal
        loan_amount,
        annual_interest_rate / 100,  # convert % to decimal
        loan_term_years,
        years,
        annual_inflation / 100,  # convert % to decimal
    )

    # --- Plot over time ---
    st.subheader("House & Mortgage Projection")
    col1, col2 = st.columns([4, 1])

    with col2:
        st.write("### Toggle Lines")
        show_house_value = st.checkbox("House value", value=True)
        show_house_value_real = st.checkbox("House value (Real)", value=True)
        show_balance = st.checkbox("Remaining loan balance", value=True)
        show_balance_real = st.checkbox("Remaining loan balance (Real)", value=True)
        show_equity = st.checkbox("Equity", value=True)
        show_equity_real = st.checkbox("Equity (Real)", value=True)

    columns_to_plot = []
    if show_house_value:
        columns_to_plot.append("house_value")
    if show_house_value_real:
        columns_to_plot.append("house_value_real")
    if show_balance:
        columns_to_plot.append("remaining_balance")
    if show_balance_real:
        columns_to_plot.append("remaining_balance_real")
    if show_equity:
        columns_to_plot.append("equity")
    if show_equity_real:
        columns_to_plot.append("equity_real")

    with col1:
        if columns_to_plot:
            fig = px.line(
                df.to_pandas(),
                x="month",
                y=columns_to_plot,
                labels={"value": "Amount", "month": "Month"},
                title="House & Mortgage Projection",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Select at least one line to display on the plot.")

    # --- Show table ---
    st.subheader("Yearly Projection")
    df_yearly = df.filter(pl.col("month") % 12 == 0)
    st.dataframe(df_yearly, width=1800)


if __name__ == "__main__":
    main()
