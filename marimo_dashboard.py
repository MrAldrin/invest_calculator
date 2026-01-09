import marimo

__generated_with = "0.19.0"
app = marimo.App(
    width="columns",
    app_title="Invest calculator",
    layout_file="layouts/marimo_dashboard.grid.json",
)

with app.setup:
    import marimo as mo
    import polars as pl
    import plotly.express as px
    import polars.selectors as cs
    from millify import millify

    from utils import combined_property_and_stocks


@app.cell
def _():
    mo.md("""
    ## Shared Parameters
    """)
    return


@app.cell
def _():
    # Common Parameters
    _show_value = True
    time_horizon_years = mo.ui.slider(
        start=1,
        stop=25,
        value=15,
        show_value=_show_value,
        full_width=True,
        label="Projection horizon (years)",
    )
    annual_inflation = mo.ui.slider(
        start=0.0,
        stop=10.0,
        value=2.0,
        step=0.1,
        show_value=_show_value,
        full_width=True,
        label="Annual inflation (%)",
    )
    annual_stock_return = mo.ui.slider(
        start=0.0,
        stop=15.0,
        value=10.0,
        step=0.5,
        show_value=_show_value,
        full_width=True,
        label="Annual stock return (%)",
    )
    annual_property_appreciation = mo.ui.slider(
        start=0.0,
        stop=8.0,
        value=5.0,
        step=0.1,
        show_value=_show_value,
        full_width=True,
        label="Annual house value change (%)",
    )
    annual_interest_rate = mo.ui.slider(
        start=0.0,
        stop=10.0,
        value=4.0,
        step=0.1,
        show_value=_show_value,
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
    annual_property_appreciation,
    annual_stock_return,
    effective_rate,
    rentefradrag,
    scenario_a,
    scenario_b,
    time_horizon_years,
):
    # Calculate Scenario A
    scenario1_df = combined_property_and_stocks(
        property_price=scenario_a["property_price"].value,
        annual_property_appreciation=annual_property_appreciation.value / 100,
        loan_amount=scenario_a["loan_amount"].value,
        annual_interest_rate=effective_rate / 100,
        loan_term_years=scenario_a["loan_term"].value,
        initial_stock_investment=scenario_a["initial_stock"].value,
        monthly_stock_investment=scenario_a["monthly_stock"].value,
        annual_stock_return=annual_stock_return.value / 100,
        time_horizon_years=time_horizon_years.value,
        annual_inflation=annual_inflation.value / 100,
        rentefradrag=rentefradrag.value,
    )

    # Calculate Scenario B
    scenario2_df = combined_property_and_stocks(
        property_price=scenario_b["property_price"].value,
        annual_property_appreciation=annual_property_appreciation.value / 100,
        loan_amount=scenario_b["loan_amount"].value,
        annual_interest_rate=effective_rate / 100,
        loan_term_years=scenario_b["loan_term"].value,
        initial_stock_investment=scenario_b["initial_stock"].value,
        monthly_stock_investment=scenario_b["monthly_stock"].value,
        annual_stock_return=annual_stock_return.value / 100,
        time_horizon_years=time_horizon_years.value,
        annual_inflation=annual_inflation.value / 100,
        rentefradrag=rentefradrag.value,
    )
    return scenario1_df, scenario2_df


@app.cell
def _():
    mo.md("""
    ## Net Worth Comparison
    """)
    return


@app.cell
def _():
    mo.md(r"""
    ## UI - components
    """)
    return


@app.function
def scenario_end_stats(df_scenario):
    # Compute the values (similar to your Streamlit code)
    total_net_worth = millify(df_scenario["total_net_worth"][-1], precision=2)
    stock_equity = millify(df_scenario["stock_equity"][-1], precision=2)
    house_equity = millify(df_scenario["property_equity"][-1], precision=2)
    property_value = millify(df_scenario["property_value"][-1], precision=2)

    # Build “metric cards” with markdown
    cards = [
        mo.md(f"**Total net worth**  \n{total_net_worth}"),
        mo.md(f"**Stock equity**  \n{stock_equity}"),
        mo.md(f"**House equity**  \n{house_equity}"),
        mo.md(f"**Property value**  \n{property_value}"),
    ]

    # Horizontal row, centered-like layout
    return mo.hstack(cards)


@app.cell
def _():
    def stats_components(
        df_scenario: pl.DataFrame,
        monthly_stock_investment: float,
        monthly_property_maintenance: float,
        property_price: float,
        loan_amount: float,
        initial_stock_investment: float,
    ):
        # Logic remains the same
        initial_equity = property_price - loan_amount + initial_stock_investment

        # Calculate values
        loan_payment = df_scenario["loan_payment"][1]
        net_cost = df_scenario["net_cost"][1]

        total_payment = (
            monthly_stock_investment + loan_payment + monthly_property_maintenance
        )
        real_total_payment = (
            monthly_stock_investment + net_cost + monthly_property_maintenance
        )

        # Marimo Stat objects (equivalent to st.metric)
        # Using fnd/millify logic inside the value
        m0 = mo.stat(label=f"Initial equity", value=millify(initial_equity, precision=2))

        # Column 1 components
        m1 = mo.stat(label="Monthly loan payment", value=millify(loan_payment, precision=1))
        m2 = mo.stat(
            label="Monthly payment",
            value=millify(total_payment, precision=1),
            caption="Stock + loan + other costs",
        )

        # Column 2 components
        m3 = mo.stat(
            label="Real loan cost",
            value=millify(net_cost, precision=1),
            caption="After tax deduction",
        )
        m4 = mo.stat(
            label="Real monthly payment",
            value=millify(real_total_payment, precision=1),
            caption="Stock + net loan + other costs",
        )

        # Layout using hstack and vstack
        return mo.vstack(
            [
                m0,
                mo.hstack(
                    [
                        mo.vstack([mo.md("### Monthly costs"), m1, m2]).style(
                            {"padding": "0.rem"}
                        ),
                        mo.vstack([mo.md("### Costs after tax deduction"), m3, m4]).style(
                            {"padding": "0rem"}
                        ),
                    ],
                    justify="start",
                ),
            ]
        )


    def stats_components_wrapper(df_scenario: pl.DataFrame, scenario_object):
        return stats_components(
            df_scenario=df_scenario,
            monthly_stock_investment=scenario_object["monthly_stock"].value,
            monthly_property_maintenance=scenario_object[
                "monthly_property_maintenance"
            ].value,
            property_price=scenario_object["property_price"].value,
            loan_amount=scenario_object["loan_amount"].value,
            initial_stock_investment=scenario_object["initial_stock"].value,
        )
    return (stats_components_wrapper,)


@app.cell(column=1)
def _(scenario1_df, scenario2_df):
    # Show comparison stats
    difference = scenario1_df["total_net_worth"][-1] - scenario2_df["total_net_worth"][-1]
    mo.md(f"""
    ## Final Values Compared

    **Difference (Scenario A - B):** {millify(difference, precision=1)}
    """)
    return


@app.cell(column=2)
def _():
    mo.md("""
    # Investment Comparison Calculator
    """)
    return


@app.cell
def _():
    def create_scenario_sliders(suffix: str):
        return mo.ui.dictionary(
            {
                "property_price": mo.ui.slider(
                    start=1_000_000,
                    stop=10_000_000,
                    value=3_000_000,
                    step=100_000,
                    show_value=False,
                    full_width=True,
                    label=f"Property price {suffix}",
                ),
                "loan_amount": mo.ui.slider(
                    start=0,
                    stop=8_000_000,
                    value=2_000_000,
                    step=100_000,
                    full_width=True,
                    label=f"Loan amount {suffix}",
                ),
                "loan_term": mo.ui.slider(
                    start=1,
                    stop=30,
                    value=25,
                    full_width=True,
                    label=f"Loan term (years) {suffix}",
                ),
                "initial_stock": mo.ui.slider(
                    start=0,
                    stop=2_000_000,
                    value=500_000,
                    step=50_000,
                    full_width=True,
                    label=f"Initial stock investment {suffix}",
                ),
                "monthly_stock": mo.ui.slider(
                    start=0,
                    stop=50_000,
                    value=5_000,
                    step=1_000,
                    full_width=True,
                    label=f"Monthly stock investment {suffix}",
                ),
                "monthly_property_maintenance": mo.ui.slider(
                    start=0,
                    stop=20_000,
                    value=5_000,
                    step=1_000,
                    full_width=True,
                    label=f"Monthly property maintenance costs {suffix}",
                ),
            }
        )


    def render_scenario(scenario_dict):
        return mo.vstack(
            [
                mo.hstack(
                    [
                        slider,
                        mo.md(f"{millify(slider.value, precision=1)}").style(
                            {
                                "display": "flex",
                                "justify-content": "flex-end",  # Right align
                                "align-items": "flex-end",  # Bottom align
                                "height": "100%",  # Ensure it fills the row height
                            }
                        ),
                    ],
                    widths=[3, 1],
                )
                for slider in scenario_dict.values()
            ]
        )
    return create_scenario_sliders, render_scenario


@app.cell
def _(create_scenario_sliders):
    # Initialize the two scenarios
    scenario_a = create_scenario_sliders("A")
    scenario_b = create_scenario_sliders("B")
    return scenario_a, scenario_b


@app.cell(column=3)
def _():
    mo.md(r"""
    # Shared values
    """)
    return


@app.cell
def _(
    annual_inflation,
    annual_interest_rate,
    annual_property_appreciation,
    annual_stock_return,
    effective_rate,
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


@app.cell(column=4)
def _():
    mo.md("""
    ## Scenario A
    """)
    return


@app.cell
def _(render_scenario, scenario_a):
    render_scenario(scenario_a)
    return


@app.cell
def _(scenario1_df, scenario_a, stats_components_wrapper):
    stats_components_wrapper(df_scenario=scenario1_df, scenario_object=scenario_a)
    return


@app.cell
def _(scenario1_df):
    mo.vstack([mo.md("## Alternative A:"), scenario_end_stats(df_scenario=scenario1_df)])
    return


@app.cell(column=5)
def _():
    mo.md("""
    ## Scenario B
    """)
    return


@app.cell
def _(render_scenario, scenario_b):
    render_scenario(scenario_b)
    return


@app.cell
def _(scenario2_df, scenario_b, stats_components_wrapper):
    stats_components_wrapper(df_scenario=scenario2_df, scenario_object=scenario_b)
    return


@app.cell
def _(scenario2_df):
    mo.vstack([mo.md("## Alternative B:"), scenario_end_stats(df_scenario=scenario2_df)])
    return


@app.cell(column=6)
def _(scenario1_df, scenario2_df):
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
def _(scenario1_df, scenario2_df):
    numeric_cols = scenario1_df.select(cs.numeric()).columns

    scenario1_yearly = scenario1_df.filter(
        (pl.col("month") % 12 == 0) | (pl.col("month") == 1)
    )
    scenario2_yearly = scenario2_df.filter(
        (pl.col("month") % 12 == 0) | (pl.col("month") == 1)
    )
    mo.vstack(
        [
            mo.md("## Detailed Data (Yearly)"),
            mo.md("**Scenario A:**"),
            mo.ui.table(
                scenario1_yearly,
                format_mapping={col: "{:_.0f}" for col in numeric_cols},
                show_column_summaries=False,
                show_data_types=False,
            ),
            mo.md("**Scenario B:**"),
            mo.ui.table(
                scenario2_yearly,
                format_mapping={col: "{:_.0f}" for col in numeric_cols},
                show_column_summaries=False,
                show_data_types=False,
            ),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
