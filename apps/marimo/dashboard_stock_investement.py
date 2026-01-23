import marimo

__generated_with = "0.19.4"
app = marimo.App(
    width="columns",
    layout_file="layouts/dashboard_stock_investement.grid.json",
)

with app.setup:
    import micropip


@app.cell
def _(mo):
    mo.md(r"""
    # App elements
    """)
    return


@app.cell
def _(FULL_WIDTH, SHOW_VALUE, mo):
    time_slider = mo.ui.slider(
        start=1,
        stop=25,
        value=20,
        debounce=True,
        show_value=SHOW_VALUE,
        full_width=FULL_WIDTH,
        label="Projection horizon (years)",
    )
    time_slider
    return (time_slider,)


@app.cell
def _(plot):
    figure = plot()
    figure
    return


@app.cell
def _(add_button, alternatives, mo, remove_button, render_scenario_sliders):
    mo.vstack(
        [
            *[
                render_scenario_sliders(alternative, i)
                for i, alternative in enumerate(alternatives)
            ],
            mo.hstack([add_button, remove_button]),
        ]
    )
    return


@app.cell(column=1)
def _(mo):
    mo.md(r"""
    # Code that runs
    """)
    return


@app.cell
def _(mo):
    get_scenarios, set_scenarios = mo.state(
        [
            {
                "initial_stock_investment": 500_000,
                "monthly_stock_investment": 5_000,
                "annual_stock_return": 10.0,
                "annual_inflation": 2.0,
            }
        ]
    )
    return get_scenarios, set_scenarios


@app.cell
def _(mo, set_scenarios):
    add_button = mo.ui.button(
        label="Add alternative",
        on_change=lambda _: set_scenarios(
            lambda scenarios: scenarios
            + [
                scenarios[-1].copy()
                if scenarios
                else {
                    "initial_stock_investment": 500_000,
                    "monthly_stock_investment": 5_000,
                    "annual_stock_return": 10.0,
                    "annual_inflation": 2.0,
                }
            ]
        ),
    )

    remove_button = mo.ui.button(
        label="Remove alternative",
        on_change=lambda _: set_scenarios(
            lambda scenarios: scenarios[:-1] if scenarios else scenarios
        ),
    )
    return add_button, remove_button


@app.cell
def _(create_scenario_sliders, get_scenarios, mo):
    scenarios = get_scenarios()
    alternatives = mo.ui.array(
        [create_scenario_sliders(s, i) for i, s in enumerate(scenarios)]
    )
    return (alternatives,)


@app.cell
def _(alternatives, pl, time_slider, wrapper_stock_investment_monthly):
    df_alternatives = []
    for i, alternative in enumerate(alternatives):
        df = wrapper_stock_investment_monthly(alternative, time_slider)
        df = df.with_columns(pl.lit(f"Alternative {i + 1}").alias("Alternative"))
        df_alternatives.append(df)
    return (df_alternatives,)


@app.cell(column=2)
def _(mo):
    mo.md(r"""
    # Functions and imports
    """)
    return


@app.cell
def _():
    # for bulishing on github pages it is recommended to have this in its own cell
    import marimo as mo
    return (mo,)


@app.cell
async def _():
    # this can apparently not be in the setup cell
    await micropip.install("polars")
    import polars as pl
    import altair as alt
    return alt, pl


@app.cell
def _():
    COLORS = [
        "#3498db",  # blue
        "#e74c3c",  # red
        "#9b59b6",  # purple
        "#f39c12",  # orange
        "#2ecc71",  # green
        "#1abc9c",  # turquoise
        "#e67e22",  # dark orange
        "#95a5a6",  # gray
    ]

    SHOW_VALUE = True
    FULL_WIDTH = True
    return COLORS, FULL_WIDTH, SHOW_VALUE


@app.cell
def _(COLORS, mo):
    def render_scenario_sliders(scenario_dict, index):
        color = COLORS[index % len(COLORS)]
        rendered_sliders = mo.hstack(
            [
                scenario_dict["initial_stock_investment"],
                scenario_dict["monthly_stock_investment"],
                scenario_dict["annual_stock_return"],
                scenario_dict["annual_inflation"],
            ]
        )
        # return rendered_sliders
        colored_sliders = mo.vstack([rendered_sliders]).style(
            {
                "border-left": f"4px solid {color}",
                "padding-left": "10px",
                "margin": "10px 0",
            }
        )
        return colored_sliders
    return (render_scenario_sliders,)


@app.cell
def _(mo, set_scenarios):
    def create_scenario_sliders(values, color_index):
        _show_value = True
        _full_width = True
        slider_dict = mo.ui.dictionary(
            {
                "initial_stock_investment": mo.ui.slider(
                    start=0,
                    stop=2_000_000,
                    value=values["initial_stock_investment"],
                    step=50_000,
                    debounce=True,
                    show_value=_show_value,
                    full_width=_full_width,
                    label=f"Initial stock investment",
                ),
                "monthly_stock_investment": mo.ui.slider(
                    start=0,
                    stop=50_000,
                    value=values["monthly_stock_investment"],
                    step=1_000,
                    debounce=True,
                    show_value=_show_value,
                    full_width=_full_width,
                    label=f"Monthly stock investment",
                ),
                "annual_stock_return": mo.ui.slider(
                    start=0.0,
                    stop=15.0,
                    value=values["annual_stock_return"],
                    step=0.5,
                    debounce=True,
                    show_value=_show_value,
                    full_width=_full_width,
                    label="Annual stock return (%)",
                ),
                "annual_inflation": mo.ui.slider(
                    start=0.0,
                    stop=10.0,
                    value=values["annual_inflation"],
                    step=0.1,
                    debounce=True,
                    show_value=_show_value,
                    full_width=_full_width,
                    label="Annual inflation (%)",
                ),
            },
            # Write changes back to state
            on_change=lambda new_vals: set_scenarios(
                lambda scenarios: [
                    (new_vals if i == color_index else s) for i, s in enumerate(scenarios)
                ]
            ),
        )
        return slider_dict
    return (create_scenario_sliders,)


@app.cell
def _(COLORS, alt, df_alternatives, pl):
    def plot():
        # Combine all dataframes
        full_df = pl.concat(df_alternatives)

        # Balance line
        balance = (
            alt.Chart(full_df)
            .mark_line()
            .encode(
                x=alt.X("month:Q", title="Month"),
                y=alt.Y("balance:Q", title="Amount"),
                color=alt.Color(
                    "Alternative:N",
                    scale=alt.Scale(range=COLORS[: len(df_alternatives)]),
                    legend=alt.Legend(title="Scenario"),
                ),
                tooltip=["Alternative:N", "month:Q", "balance:Q"],
            )
        )

        # Returns line (dashed)
        returns = (
            alt.Chart(full_df)
            .mark_line(strokeDash=[5, 5])
            .encode(
                x="month:Q",
                y="returns_cum:Q",
                # CHANGED: Same color encoding pattern
                color=alt.Color(
                    "Alternative:N",
                    scale=alt.Scale(range=COLORS[: len(df_alternatives)]),
                    legend=None,
                ),  # Hide legend for this layer
                tooltip=["Alternative:N", "month:Q", "returns_cum:Q"],
            )
        )

        # Contributions line (dotted)
        contributions = (
            alt.Chart(full_df)
            .mark_line(strokeDash=[2, 2])
            .encode(
                x="month:Q",
                y="contributions_cum:Q",
                # CHANGED: Same color encoding pattern
                color=alt.Color(
                    "Alternative:N",
                    scale=alt.Scale(range=COLORS[: len(df_alternatives)]),
                    legend=None,
                ),  # Hide legend for this layer
                tooltip=["Alternative:N", "month:Q", "contributions_cum:Q"],
            )
        )

        # Combine all charts
        chart = (
            (balance + returns + contributions)
            .properties(
                title="Portfolio Projections - All Alternatives", width=600, height=400
            )
            .interactive()
        )

        return chart
    return (plot,)


@app.cell
def _(stock_investment_monthly):
    def wrapper_stock_investment_monthly(sliders, time_slider):
        df = stock_investment_monthly(
            initial_investment=sliders["initial_stock_investment"].value,
            monthly_contribution=sliders["monthly_stock_investment"].value,
            annual_return=sliders["annual_stock_return"].value / 100,
            years=time_slider.value,
            annual_inflation=sliders["annual_inflation"].value / 100,
        )
        return df
    return (wrapper_stock_investment_monthly,)


@app.cell(column=3)
def _(mo):
    mo.md(r"""
    # Functions that i have/had in src/utils.py
    """)
    return


@app.cell
def _(pl):
    def apply_inflation(
        df: pl.DataFrame, annual_inflation: float, columns: list[str]
    ) -> pl.DataFrame:
        if annual_inflation == 0.0:
            return df

        monthly_inflation = (1 + annual_inflation) ** (1 / 12) - 1
        # Assumes df has a "month" column starting at 0. This speeds up computation.
        inflation_factor = (1 + monthly_inflation) ** pl.col("month")
        df = df.with_columns(
            [(pl.col(col) / inflation_factor).alias(col) for col in columns]
        )

        return df
    return (apply_inflation,)


@app.cell
def _(apply_inflation, pl):
    def stock_investment_monthly(
        initial_investment: float,
        monthly_contribution: float,
        annual_return: float,
        years: int,
        annual_inflation: float = 0.0,
        tax_rate: float = 0.3784,  # 37.84% tax on returns
    ) -> pl.DataFrame:
        n_months = years * 12
        monthly_return = (1 + annual_return) ** (1 / 12) - 1

        # Create base dataframe with months
        df = pl.DataFrame(
            {
                "month": pl.arange(0, n_months + 1, eager=True),
            }
        )

        df = (
            df.with_columns(
                [
                    (pl.col("month") // 12).alias("year"),
                    # Balance calculation using compound interest formula
                    (
                        initial_investment * ((1 + monthly_return) ** pl.col("month"))
                        + monthly_contribution
                        * (((1 + monthly_return) ** pl.col("month") - 1) / monthly_return)
                    ).alias("balance"),
                    # Contributions: simple linear growth
                    (initial_investment + monthly_contribution * pl.col("month")).alias(
                        "contributions_cum"
                    ),
                ]
            )
            .with_columns(
                [
                    (pl.col("balance") - pl.col("contributions_cum")).alias("returns_cum"),
                ]
            )
            .with_columns(
                [
                    (pl.col("returns_cum") * (1 - tax_rate)).alias("returns_after_tax"),
                    (
                        pl.col("contributions_cum") + pl.col("returns_cum") * (1 - tax_rate)
                    ).alias("stock_equity"),
                ]
            )
        )
        df = apply_inflation(
            df,
            annual_inflation,
            [
                "balance",
                "contributions_cum",
                "returns_cum",
                "returns_after_tax",
                "stock_equity",
            ],
        )
        return df
    return (stock_investment_monthly,)


if __name__ == "__main__":
    app.run()
