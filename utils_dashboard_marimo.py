import marimo

__generated_with = "0.18.4"
app = marimo.App(
    width="columns",
    app_title="Invest calculator",
    layout_file="layouts/utils_dashboard_marimo.grid.json",
)


@app.cell(column=0)
def _():
    import marimo as mo
    import plotly.express as px
    import polars as pl
    import polars.selectors as cs
    from millify import millify

    from utils import combined_property_and_stocks
    from utils_dashboard import scenario_end_stats, scenario_sliders, stats_components

    return combined_property_and_stocks, cs, millify, mo, pl, px


@app.cell
def _(mo):
    mo.md("""
    ## Shared Parameters
    """)
    return


@app.cell
def _(mo):
    # Common Parameters
    time_horizon_years = mo.ui.slider(
        start=1,
        stop=25,
        value=15,
        show_value=True,
        full_width=True,
        label="Projection horizon (years)",
    )
    annual_inflation = mo.ui.slider(
        start=0.0,
        stop=10.0,
        value=2.0,
        step=0.1,
        show_value=True,
        full_width=True,
        label="Annual inflation (%)",
    )
    annual_stock_return = mo.ui.slider(
        start=0.0,
        stop=15.0,
        value=10.0,
        step=0.5,
        show_value=True,
        full_width=True,
        label="Annual stock return (%)",
    )
    annual_property_appreciation = mo.ui.slider(
        start=0.0,
        stop=8.0,
        value=5.0,
        step=0.1,
        show_value=True,
        full_width=True,
        label="Annual house value change (%)",
    )
    annual_interest_rate = mo.ui.slider(
        start=0.0,
        stop=10.0,
        value=4.0,
        step=0.1,
        show_value=True,
        full_width=True,
        label="Mortgage interest rate (%)",
    )
    rentefradrag = mo.ui.checkbox(
        value=True, label="Include rentefradrag (22% tax deduction on interest)"
    )
    return (
        annual_inflation,
        annual_interest_rate,
        annual_property_appreciation,
        annual_stock_return,
        rentefradrag,
        time_horizon_years,
    )


@app.cell
def _(annual_interest_rate, rentefradrag):
    if rentefradrag.value:
        effective_rate = annual_interest_rate.value * (1 - 0.22)
    else:
        effective_rate = annual_interest_rate.value
    return (effective_rate,)


@app.cell
def _(
    annual_inflation,
    annual_interest_rate,
    annual_property_appreciation,
    annual_stock_return,
    effective_rate,
    mo,
    rentefradrag,
    time_horizon_years,
):
    mo.vstack(
        [
            time_horizon_years,
            annual_inflation,
            annual_stock_return,
            annual_property_appreciation,
            annual_interest_rate,
            mo.hstack(
                [
                    rentefradrag,
                    mo.md(f"**Effective interest rate:** {effective_rate:.2f}%"),
                ]
            ),
        ]
    )
    return


@app.cell
def _(
    annual_inflation,
    annual_property_appreciation,
    annual_stock_return,
    combined_property_and_stocks,
    effective_rate,
    initial_stock_investment_1,
    initial_stock_investment_2,
    loan_amount_1,
    loan_amount_2,
    loan_term_years_1,
    loan_term_years_2,
    monthly_stock_investment_1,
    monthly_stock_investment_2,
    property_price_1,
    property_price_2,
    rentefradrag,
    time_horizon_years,
):
    # Calculate Scenario A
    scenario1_df = combined_property_and_stocks(
        property_price=property_price_1.value,
        annual_property_appreciation=annual_property_appreciation.value / 100,
        loan_amount=loan_amount_1.value,
        annual_interest_rate=effective_rate / 100,
        loan_term_years=loan_term_years_1.value,
        initial_stock_investment=initial_stock_investment_1.value,
        monthly_stock_investment=monthly_stock_investment_1.value,
        annual_stock_return=annual_stock_return.value / 100,
        time_horizon_years=time_horizon_years.value,
        annual_inflation=annual_inflation.value / 100,
        rentefradrag=rentefradrag.value,
    )

    # Calculate Scenario B
    scenario2_df = combined_property_and_stocks(
        property_price=property_price_2.value,
        annual_property_appreciation=annual_property_appreciation.value / 100,
        loan_amount=loan_amount_2.value,
        annual_interest_rate=effective_rate / 100,
        loan_term_years=loan_term_years_2.value,
        initial_stock_investment=initial_stock_investment_2.value,
        monthly_stock_investment=monthly_stock_investment_2.value,
        annual_stock_return=annual_stock_return.value / 100,
        time_horizon_years=time_horizon_years.value,
        annual_inflation=annual_inflation.value / 100,
        rentefradrag=rentefradrag.value,
    )
    return scenario1_df, scenario2_df


@app.cell
def _(mo):
    mo.md("""
    ## Net Worth Comparison
    """)
    return


@app.cell
def _(pl, px, scenario1_df, scenario2_df):
    # Prepare plot data
    plot_df = pl.DataFrame(
        {
            "month": scenario1_df["month"],
            "scenario_A": scenario1_df["total_net_worth"],
            "scenario_B": scenario2_df["total_net_worth"],
        }
    ).with_columns((pl.col("scenario_A") - pl.col("scenario_B")).alias("scenario_diff"))

    # Create plot
    fig = px.line(
        plot_df,
        x="month",
        y=["scenario_A", "scenario_B", "scenario_diff"],
        labels={"value": "Net Worth", "month": "Years"},
        title="Investment Scenarios Comparison",
        color_discrete_sequence=px.colors.qualitative.Plotly,
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

    fig
    return


@app.cell
def _(millify, mo, scenario1_df, scenario2_df):
    # Show comparison stats
    difference = (
        scenario1_df["total_net_worth"][-1] - scenario2_df["total_net_worth"][-1]
    )
    mo.md(f"""
    ## Final Values Compared

    **Difference (Scenario A - B):** {millify(difference, precision=1)}
    """)
    return


@app.cell
def _(cs, mo, pl, scenario1_df, scenario2_df):
    mo.md("## Detailed Data (Yearly)")

    numeric_cols = scenario1_df.select(cs.numeric()).columns

    scenario1_yearly = scenario1_df.filter(
        (pl.col("month") % 12 == 0) | (pl.col("month") == 1)
    )
    scenario2_yearly = scenario2_df.filter(
        (pl.col("month") % 12 == 0) | (pl.col("month") == 1)
    )

    mo.vstack(
        [
            mo.md("**Scenario A:**"),
            mo.ui.table(scenario1_yearly),
            mo.md("**Scenario B:**"),
            mo.ui.table(scenario2_yearly),
        ]
    )
    return


@app.cell(column=1)
def _(mo):
    mo.md("""
    # Investment Comparison Calculator
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Scenario A
    """)
    return


@app.cell
def _(mo):
    # Scenario A Parameters
    property_price_1 = mo.ui.slider(
        start=1_000_000,
        stop=10_000_000,
        value=3_000_000,
        step=100_000,
        show_value=False,
        full_width=True,
        label="Property price A",
    )
    loan_amount_1 = mo.ui.slider(
        start=0,
        stop=8_000_000,
        value=2_000_000,
        step=100_000,
        # show_value=True,
        full_width=True,
        label="Loan amount A",
    )
    loan_term_years_1 = mo.ui.slider(
        start=1,
        stop=30,
        value=25,
        # show_value=True,
        full_width=True,
        label="Loan term (years) A",
    )
    initial_stock_investment_1 = mo.ui.slider(
        start=0,
        stop=2_000_000,
        value=500_000,
        step=50_000,
        # show_value=True,
        full_width=True,
        label="Initial stock investment A",
    )
    monthly_stock_investment_1 = mo.ui.slider(
        start=0,
        stop=50_000,
        value=5_000,
        step=1_000,
        # show_value=True,
        full_width=True,
        label="Monthly stock investment A",
    )
    return (
        initial_stock_investment_1,
        loan_amount_1,
        loan_term_years_1,
        monthly_stock_investment_1,
        property_price_1,
    )


@app.cell
def _(
    initial_stock_investment_1,
    loan_amount_1,
    loan_term_years_1,
    mo,
    monthly_stock_investment_1,
    property_price_1,
):
    widths = [4, 1]
    mo.vstack(
        items=[
            mo.hstack(
                [
                    # Left side: Slider
                    slider,
                    # Right side: Value aligned right within its allocated width
                    mo.md(f"**{slider.value:_}**").style({"text-align": "right"}),
                ],
                widths=widths,
                justify="space-between",
            )
            for slider in [
                property_price_1,
                loan_amount_1,
                loan_term_years_1,
                initial_stock_investment_1,
                monthly_stock_investment_1,
            ]
        ]
    )
    return (widths,)


@app.cell(column=2)
def _(mo):
    mo.md("""
    ## Scenario B
    """)
    return


@app.cell
def _(mo):
    # Scenario B Parameters
    property_price_2 = mo.ui.slider(
        start=1_000_000,
        stop=10_000_000,
        value=3_000_000,
        step=100_000,
        show_value=False,
        full_width=True,
        label="Property price B",
    )
    loan_amount_2 = mo.ui.slider(
        start=0,
        stop=8_000_000,
        value=2_000_000,
        step=100_000,
        # show_value=True,
        full_width=True,
        label="Loan amount B",
    )
    loan_term_years_2 = mo.ui.slider(
        start=1,
        stop=30,
        value=25,
        # show_value=True,
        full_width=True,
        label="Loan term (years) B",
    )
    initial_stock_investment_2 = mo.ui.slider(
        start=0,
        stop=2_000_000,
        value=500_000,
        step=50_000,
        # show_value=True,
        full_width=True,
        label="Initial stock investment B",
    )
    monthly_stock_investment_2 = mo.ui.slider(
        start=0,
        stop=50_000,
        value=5_000,
        step=1_000,
        # show_value=True,
        full_width=True,
        label="Monthly stock investment B",
    )
    return (
        initial_stock_investment_2,
        loan_amount_2,
        loan_term_years_2,
        monthly_stock_investment_2,
        property_price_2,
    )


@app.cell
def _(
    initial_stock_investment_2,
    loan_amount_2,
    loan_term_years_2,
    mo,
    monthly_stock_investment_2,
    property_price_2,
    widths,
):
    mo.vstack(
        items=[
            mo.hstack(
                [
                    # Left side: Slider
                    slider,
                    # Right side: Value aligned right within its allocated width
                    mo.md(f"**{slider.value:_}**").style({"text-align": "right"}),
                ],
                widths=widths,
                justify="space-between",
            )
            for slider in [
                property_price_2,
                loan_amount_2,
                loan_term_years_2,
                initial_stock_investment_2,
                monthly_stock_investment_2,
            ]
        ]
    )
    return


if __name__ == "__main__":
    app.run()
