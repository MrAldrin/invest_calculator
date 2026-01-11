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
    from utils import stock_investment_monthly
    import plotly.graph_objects as go


@app.cell
def _():
    COLORS = [
        "#2ecc71",  # green
        "#3498db",  # blue
        "#e74c3c",  # red
        "#f39c12",  # orange
        "#9b59b6",  # purple
        "#1abc9c",  # turquoise
        "#e67e22",  # dark orange
        "#95a5a6",  # gray
    ]
    return (COLORS,)


@app.cell
def _(COLORS):
    def create_scenario_sliders(color_index=0):
        _show_value = True
        _full_width = True
        color = COLORS[color_index % len(COLORS)]
        slider_dict = mo.ui.dictionary(
            {
                "initial_stock_investment": mo.ui.slider(
                    start=0,
                    stop=2_000_000,
                    value=500_000,
                    step=50_000,
                    debounce=True,
                    show_value=_show_value,
                    full_width=_full_width,
                    label=f"Initial stock investment",
                ),
                "monthly_stock_investment": mo.ui.slider(
                    start=0,
                    stop=50_000,
                    value=5_000,
                    step=1_000,
                    debounce=True,
                    show_value=_show_value,
                    full_width=_full_width,
                    label=f"Monthly stock investment",
                ),
                "annual_stock_return": mo.ui.slider(
                    start=0.0,
                    stop=15.0,
                    value=10.0,
                    step=0.5,
                    debounce=True,
                    show_value=_show_value,
                    full_width=_full_width,
                    label="Annual stock return (%)",
                ),
                "annual_inflation": mo.ui.slider(
                    start=0.0,
                    stop=10.0,
                    value=2.0,
                    step=0.1,
                    debounce=True,
                    show_value=_show_value,
                    full_width=_full_width,
                    label="Annual inflation (%)",
                ),
                "time_horizon_years": mo.ui.slider(
                    start=1,
                    stop=25,
                    value=15,
                    debounce=True,
                    show_value=_show_value,
                    full_width=_full_width,
                    label="Projection horizon (years)",
                ),
            }
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
                scenario_dict["time_horizon_years"],
            ]
        )
        # return rendered_sliders
        return mo.vstack([rendered_sliders]).style(
            {
                "border-left": f"4px solid {color}",
                "padding-left": "10px",
                "margin": "10px 0",
            }
        )
    return (render_scenario_sliders,)


@app.function
def wrapper_stock_investment_monthly(sliders):
    df = stock_investment_monthly(
        initial_investment=sliders["initial_stock_investment"].value,
        monthly_contribution=sliders["monthly_stock_investment"].value,
        annual_return=sliders["annual_stock_return"].value / 100,
        years=sliders["time_horizon_years"].value,
        annual_inflation=sliders["annual_inflation"].value / 100,
    )
    return df


@app.cell
def _(alternatives):
    df_alternatives = []
    for i, alt in enumerate(alternatives):
        df = wrapper_stock_investment_monthly(alt)
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
    # how many lines (each line = one slider here, but you can use more)
    get_alts, set_alts = mo.state([0])
    return get_alts, set_alts


@app.cell
def _(set_alts):
    # Buttons to add/remove a line
    add_button = mo.ui.button(
        label="Add alternative",
        on_change=lambda _: set_alts(lambda lines: lines + [0]),
    )

    remove_button = mo.ui.button(
        label="Remove alternative",
        on_change=lambda _: set_alts(lambda lines: lines[:-1] if lines else lines),
    )
    return add_button, remove_button


@app.cell
def _(create_scenario_sliders, get_alts, set_alts):
    alternatives = mo.ui.array(
        [create_scenario_sliders(color_index=i) for i, _ in enumerate(get_alts())],
        on_change=lambda values: set_alts(values),
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


if __name__ == "__main__":
    app.run()
