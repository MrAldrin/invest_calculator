"""
uv run streamlit run dashboard_investment.py --server.headless true

This template is intentionally simple but production-ready:
- Core calculation in pure Python (easy to unit test)
- Monthly compounding and contributions
- Clean Streamlit UI with sliders for years, monthly investment, and annual return
- KPIs + interactive chart + optional projection table
- Clear places marked with TODOs for your future enhancements
"""

from __future__ import annotations

import altair as alt
import plotly.express as px
import polars as pl
import streamlit as st

from utils import stock_investment_monthly

# ========================
# Streamlit UI
# ========================


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

    # --- Plot balance over time ---
    st.subheader("Portfolio Projection")

    # Create columns: plot (wide) and checkboxes (narrow)
    col1, col2 = st.columns([4, 1])

    # --- Sidebar-like controls on the right ---
    with col2:
        st.write("### Toggle Lines")
        show_balance = st.checkbox("Balance", value=True)
        show_balance_real = st.checkbox("Balance (Real)", value=True)
        show_returns = st.checkbox("Returns", value=False)
        show_returns_real = st.checkbox("Returns (Real)", value=False)

    # --- Determine which columns to plot ---
    columns_to_plot = []
    if show_balance:
        columns_to_plot.append("balance")
    if show_balance_real:
        columns_to_plot.append("balance_real")
    if show_returns:
        columns_to_plot.append("returns_cum")
    if show_returns_real:
        columns_to_plot.append("returns_cum_real")  # make sure you calculate this

    # --- Plot in the left column ---
    with col1:
        if columns_to_plot:  # only plot if at least one line is selected
            fig = px.line(
                df.to_pandas(),
                x="month",
                y=columns_to_plot,
                labels={"value": "Amount", "month": "Month"},
                title="Portfolio Projection",
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

    # st.set_page_config(
    #     page_title="Investment Calculator", page_icon="📈", layout="wide"
    # )

    # st.title("📈 Investment Calculator — Starter Template")
    # st.caption("Adjust inputs on the left. The chart and KPIs update instantly.")

    # with st.sidebar:
    #     st.header("Inputs")
    #     years = st.slider("Years", min_value=1, max_value=50, value=20, step=1)
    #     monthly = st.slider(
    #         "Monthly investment", min_value=0, max_value=100000, value=15000, step=1000
    #     )
    #     rate = st.slider(
    #         "Annual return (%)", min_value=-20.0, max_value=30.0, value=7.0, step=0.1
    #     )
    #     initial = st.number_input(
    #         "Initial investment",
    #         min_value=0.0,
    #         value=10000.0,
    #         step=1000.0,
    #         format="%.2f",
    #     )
    #     timing = st.selectbox(
    #         "Contribution timing",
    #         options=["end", "begin"],
    #         index=0,
    #         help="'end' = pay at end of month; 'begin' = pay at start",
    #     )

    #     # TODO: Add optional parameters later (e.g., annual contribution increase, fees, inflation)

    # inputs = ProjectionInputs(
    #     years=years,
    #     monthly_contribution=float(monthly),
    #     annual_return_pct=float(rate),
    #     initial_investment=float(initial),
    #     contribution_timing=timing,
    # )

    # df = project_cashflows(inputs)

    # final_balance = float(df["balance"].iloc[-1])
    # total_contrib = float(df["total_contributions"].iloc[-1])
    # total_returns = float(df["total_returns"].iloc[-1])

    # kpi1, kpi2, kpi3 = st.columns(3)
    # kpi1.metric("Final value", f"{final_balance:,.0f}")
    # kpi2.metric("Total contributed", f"{total_contrib:,.0f}")
    # kpi3.metric("Total returns", f"{total_returns:,.0f}")

    # # Chart
    # line = (
    #     alt.Chart(df)
    #     .mark_line()
    #     .encode(
    #         x=alt.X("month:Q", title="Month"),
    #         y=alt.Y("balance:Q", title="Portfolio value"),
    #         tooltip=[
    #             alt.Tooltip("month", title="Month"),
    #             alt.Tooltip("balance", title="Balance", format=","),
    #         ],
    #     )
    #     .properties(height=360)
    # )
    # st.altair_chart(line, use_container_width=True)

    # with st.expander("Show projection table"):
    #     st.dataframe(
    #         df.assign(
    #             balance=df["balance"].map(lambda x: round(x, 2)),
    #             total_contributions=df["total_contributions"].map(
    #                 lambda x: round(x, 2)
    #             ),
    #             total_returns=df["total_returns"].map(lambda x: round(x, 2)),
    #         ),
    #         use_container_width=True,
    #         height=360,
    #     )

    # st.markdown("""
    # **Next steps (ideas):**
    # - Add an *annual increase* for monthly contributions (e.g., +3%/yr)
    # - Model *fees* (fixed and/or % of assets) and *taxes*
    # - Add *inflation* and show **real** (inflation-adjusted) returns
    # - Offer yearly/quarterly compounding options
    # - Add scenario comparison (e.g., optimistic/base/pessimistic)
    # - Export to CSV/Excel/PDF
    # """)
