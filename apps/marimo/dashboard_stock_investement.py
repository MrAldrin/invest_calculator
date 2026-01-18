import marimo

__generated_with = "0.19.0"
app = marimo.App(
    width="columns",
    layout_file="layouts/dashboard_stock_investement.grid.json",
)

with app.setup:
    # Initialization code that runs before all other cells
    import marimo as mo
    import polars as pl
    from millify import millify
    import plotly.express as px
    from src.utils import stock_investment_monthly
    import plotly.graph_objects as go


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
def _(COLORS, set_scenarios):
    def create_scenario_sliders(values, color_index):
        _show_value = True
        _full_width = True
        color = COLORS[color_index % len(COLORS)]
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
                # "time_horizon_years": mo.ui.slider(
                #     start=1,
                #     stop=25,
                #     value=values["time_horizon_years"],
                #     debounce=True,
                #     show_value=_show_value,
                #     full_width=_full_width,
                #     label="Projection horizon (years)",
                # ),
            },
            # Write changes back to state
            on_change=lambda new_vals: set_scenarios(
                lambda scenarios: [
                    (new_vals if i == color_index else s)
                    for i, s in enumerate(scenarios)
                ]
            ),
        )
        return slider_dict

    return (create_scenario_sliders,)


@app.cell
def _(COLORS):
    def render_scenario_sliders(scenario_dict, index):
        color = COLORS[index % len(COLORS)]
        rendered_sliders = mo.hstack(
            [
                scenario_dict["initial_stock_investment"],
                scenario_dict["monthly_stock_investment"],
                scenario_dict["annual_stock_return"],
                scenario_dict["annual_inflation"],
                # scenario_dict["time_horizon_years"],
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


@app.function
def wrapper_stock_investment_monthly(sliders, time_slider):
    df = stock_investment_monthly(
        initial_investment=sliders["initial_stock_investment"].value,
        monthly_contribution=sliders["monthly_stock_investment"].value,
        annual_return=sliders["annual_stock_return"].value / 100,
        years=time_slider.value,
        annual_inflation=sliders["annual_inflation"].value / 100,
    )
    return df


@app.cell
def _(alternatives, time_slider):
    df_alternatives = []
    for i, alt in enumerate(alternatives):
        df = wrapper_stock_investment_monthly(alt, time_slider)
        df = df.with_columns(pl.lit(f"Alternative {i + 1}").alias("scenario"))
        df_alternatives.append(df)
    return (df_alternatives,)


@app.cell
def _(COLORS, df_alternatives):
    def plot():
        fig_alternatives = go.Figure()

        for i, df in enumerate(df_alternatives):
            scenario_name = f"Alt {i + 1}"
            color = COLORS[i % len(COLORS)]

            fig_alternatives.add_trace(
                go.Scatter(
                    x=df["month"],
                    y=df["balance"],
                    name=f"{scenario_name} - Balance",
                    mode="lines",
                    line=dict(color=color),
                )
            )
            fig_alternatives.add_trace(
                go.Scatter(
                    x=df["month"],
                    y=df["returns_cum"],
                    name=f"{scenario_name} - Returns",
                    mode="lines",
                    line=dict(dash="dash", color=color),
                )
            )
            fig_alternatives.add_trace(
                go.Scatter(
                    x=df["month"],
                    y=df["contributions_cum"],
                    name=f"{scenario_name} - Contributions",
                    mode="lines",
                    line=dict(dash="dot", color=color),
                )
            )

        fig_alternatives.update_layout(
            title="Portfolio Projections - All Alternatives",
            xaxis_title="Month",
            yaxis_title="Amount",
        )
        return fig_alternatives

    return (plot,)


@app.cell
def _(plot):
    plot()
    return


@app.cell(column=1)
def _():
    get_scenarios, set_scenarios = mo.state(
        [
            {
                "initial_stock_investment": 500_000,
                "monthly_stock_investment": 5_000,
                "annual_stock_return": 10.0,
                "annual_inflation": 2.0,
                # "time_horizon_years": 15,
            }
        ]
    )
    return get_scenarios, set_scenarios


@app.cell
def _(set_scenarios):
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
                    "time_horizon_years": 15,
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
def _(create_scenario_sliders, get_scenarios):
    scenarios = get_scenarios()
    alternatives = mo.ui.array(
        [create_scenario_sliders(s, i) for i, s in enumerate(scenarios)]
    )
    return (alternatives,)


@app.cell
def _(add_button, alternatives, remove_button, render_scenario_sliders):
    mo.vstack(
        [
            *[render_scenario_sliders(alt, i) for i, alt in enumerate(alternatives)],
            mo.hstack([add_button, remove_button]),
        ]
    )
    return


@app.cell
def _(FULL_WIDTH, SHOW_VALUE):
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


if __name__ == "__main__":
    app.run()
