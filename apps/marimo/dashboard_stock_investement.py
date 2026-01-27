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
def _(mo):
    mo.md(r"""
    # Stock investment calculator
    """)
    return


@app.cell
def _(time_slider):
    time_slider
    return


@app.cell
def _(df_alternatives, plot):
    figure = plot(df_alternatives=df_alternatives)
    figure
    return


@app.cell
def _(ui_sliders_alternatives):
    ui_sliders_alternatives
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
        * 4
    )
    return get_scenarios, set_scenarios


@app.cell
def _(mo):
    get_visible_count, set_visible_count = mo.state(1)
    return get_visible_count, set_visible_count


@app.cell
def _(mo, set_visible_count):
    add_button = mo.ui.button(
        label="Add alternative",
        on_change=lambda _: set_visible_count(lambda count: min(count + 1, 5)),
    )

    remove_button = mo.ui.button(
        label="Remove alternative",
        on_change=lambda _: set_visible_count(lambda count: max(count - 1, 1)),
    )
    return add_button, remove_button


@app.cell
def _(create_scenario_sliders, get_scenarios, get_visible_count, mo):
    scenarios = get_scenarios()
    visible_count = get_visible_count()
    alternatives = mo.ui.array(
        [
            create_scenario_sliders(values=s, color_index=i)
            for i, s in enumerate(scenarios[:visible_count])
        ]
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


@app.cell
def _(mo):
    mo.md(r"""
    # Sliders
    """)
    return


@app.cell
def _(FULL_WIDTH, SHOW_VALUE, mo):
    time_slider = mo.ui.slider(
        start=1,
        stop=30,
        value=20,
        debounce=True,
        show_value=SHOW_VALUE,
        full_width=FULL_WIDTH,
        label="Projection horizon (years)",
    )
    return (time_slider,)


@app.cell
def _(
    add_button,
    alternatives,
    get_visible_count,
    mo,
    remove_button,
    render_scenario_sliders,
):
    left_buttons = []
    right_buttons = []

    if get_visible_count() < 5:
        left_buttons.append(add_button)
    if get_visible_count() > 1:
        right_buttons.append(remove_button)

    ui_sliders_alternatives = mo.vstack(
        [
            *[
                render_scenario_sliders(alternative, i)
                for i, alternative in enumerate(alternatives)
            ],
            mo.hstack(
                [
                    mo.hstack(left_buttons) if left_buttons else mo.Html(""),
                    mo.hstack(right_buttons, justify="end")
                    if right_buttons
                    else mo.Html(""),
                ]
            ),
        ]
    )
    return (ui_sliders_alternatives,)


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
    def render_scenario_sliders(scenario_dict, color_index):
        color = COLORS[color_index % len(COLORS)]
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
def _():
    import numpy as np
    import math


    def creator_step_range(min_val=1000, max_val=1e6):
        # zero is always included
        a = 1.5
        b = 3

        values = [0]

        if min_val > 0:
            magnitude = 10 ** (math.floor(math.log10(min_val)) - 1)
        else:
            magnitude = 1

        while magnitude <= max_val:
            # fine steps
            values.extend(np.arange(a * magnitude, b * magnitude, magnitude / 10))

            # coarser steps
            values.extend(np.arange(b * magnitude, a * magnitude * 10, magnitude / 2))

            magnitude *= 10

        # filter + clean
        values = np.array(values)
        values = values[(values == 0) | ((values >= min_val) & (values <= max_val))]
        return np.unique(values).tolist()
    return (creator_step_range,)


@app.cell
def _(creator_step_range, mo, set_scenarios):
    def create_scenario_sliders(values, color_index):
        _show_value = True
        _full_width = True
        slider_dict = mo.ui.dictionary(
            {
                "initial_stock_investment": mo.ui.slider(
                    steps=creator_step_range(min_val=1e4, max_val=1e7),
                    value=values["initial_stock_investment"],
                    debounce=True,
                    show_value=_show_value,
                    full_width=_full_width,
                    label=f"Initial stock investment",
                ),
                "monthly_stock_investment": mo.ui.slider(
                    steps=creator_step_range(min_val=1e2, max_val=1e6),
                    value=values["monthly_stock_investment"],
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
            # Needed to not reset sliders when an alternative is added or removed
            on_change=lambda new_vals: set_scenarios(
                lambda scenarios: [
                    (new_vals if i == color_index else s) for i, s in enumerate(scenarios)
                ]
            ),
        )
        return slider_dict
    return (create_scenario_sliders,)


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


@app.cell
def _(COLORS, alt, pl):
    def plot(df_alternatives, COLORS=COLORS):
        full_df = pl.concat(df_alternatives)
        # Transform from wide to long
        long_df = full_df.unpivot(
            index=["month", "Alternative"],
            on=["balance", "returns_cum", "contributions_cum"],
            variable_name="Metric",
            value_name="Amount",
        )
        selection = alt.selection_point(
            fields=["Alternative"], bind="legend", toggle="true"
        )
        selection_metric = alt.selection_point(
            fields=["Metric"], bind="legend", toggle="true"
        )

        chart = (
            alt.Chart(long_df)
            .mark_line()
            .encode(
                x=alt.X(
                    "month:Q",
                    title="Year",
                    axis=alt.Axis(
                        labelExpr="datum.value / 12",
                        values=list(range(0, 1000, 12)),
                        format="d",
                    ),
                ),
                y=alt.Y("Amount:Q", title="Amount"),
                color=alt.Color(
                    "Alternative:N",
                    scale=alt.Scale(range=COLORS[: len(df_alternatives)]),
                    legend=alt.Legend(title="Scenario"),
                ),
                # This creates the second legend and controls line style
                strokeDash=alt.StrokeDash(
                    "Metric:N",
                    scale=alt.Scale(
                        domain=["balance", "returns_cum", "contributions_cum"],
                        range=[[], [5, 5], [2, 2]],  # Solid, Dashed, Dotted
                    ),
                    legend=alt.Legend(title="Metric Toggle"),
                ),
                tooltip=["Alternative:N", "Metric:N", "month:Q", "Amount:Q"],
                # Apply both interactive filters
                opacity=alt.condition(
                    selection & selection_metric, alt.value(1), alt.value(0.1)
                ),
            )
            .add_params(selection, selection_metric)  # Register both legends
            .properties(
                title="Portfolio Projections - All Alternatives", width=600, height=400
            )
            .interactive()
        )

        return chart
    return (plot,)


@app.cell(column=3)
def _(mo):
    nav_menu = mo.nav_menu(
        {
            "/overview": "Overview",
            "/sales": f"{mo.icon('lucide:shopping-cart')} Sales",
            "/products": f"{mo.icon('lucide:package')} Products",
        }
    )
    return


@app.cell(column=4)
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
