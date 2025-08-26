"""
Streamlit Investment Calculator — Starter Template

How to run locally:
1) Save this file as `app.py`
2) In a terminal, run:  streamlit run app.py

This template is intentionally simple but production-ready:
- Core calculation in pure Python (easy to unit test)
- Monthly compounding and contributions
- Clean Streamlit UI with sliders for years, monthly investment, and annual return
- KPIs + interactive chart + optional projection table
- Clear places marked with TODOs for your future enhancements
"""

import polars as pl

# ========================
# Core calculation logic
# ========================


def stock_investment_monthly(
    initial_investment: float,
    monthly_contribution: float,
    annual_return: float,
    years: int,
    annual_inflation: float = 0.0,
) -> pl.DataFrame:
    n_months = years * 12
    r_monthly = annual_return / 12.0
    i_monthly = annual_inflation / 12.0

    balance = [initial_investment]
    contributions_cum = [initial_investment]
    returns_cum = [0.0]

    for m in range(1, n_months + 1):
        # previous balance grows
        interest = balance[-1] * r_monthly
        new_balance = balance[-1] + interest
        # add monthly contribution
        new_balance += monthly_contribution

        # update cumulative trackers
        balance.append(new_balance)
        contributions_cum.append(contributions_cum[-1] + monthly_contribution)
        returns_cum.append(returns_cum[-1] + interest)

    df = pl.DataFrame(
        {
            "month": [int(m) for m in range(n_months + 1)],
            "year": [int(m // 12) for m in range(n_months + 1)],
            "balance": balance,
            "contributions_cum": contributions_cum,
            "returns_cum": returns_cum,
        },
        schema={
            "month": pl.Int64,
            "year": pl.Int64,
            "balance": pl.Float64,
            "contributions_cum": pl.Float64,
            "returns_cum": pl.Float64,
        },
    )

    df = df.with_columns(
        [
            (pl.col("balance") / ((1 + i_monthly) ** pl.col("month"))).alias(
                "balance_real"
            ),
            (pl.col("contributions_cum") / ((1 + i_monthly) ** pl.col("month"))).alias(
                "contributions_real"
            ),
            (pl.col("returns_cum") / ((1 + i_monthly) ** pl.col("month"))).alias(
                "returns_cum_real"
            ),
        ]
    )
    return df


def house_value_monthly(
    initial_price: float,
    annual_value_change: float,
    years: int,
    annual_inflation: float = 0.0,
) -> pl.DataFrame:
    n_months = years * 12
    monthly_growth = (1 + annual_value_change) ** (1 / 12) - 1
    monthly_inflation = (1 + annual_inflation) ** (1 / 12) - 1

    values = [initial_price]
    for m in range(1, n_months + 1):
        new_value = values[-1] * (1 + monthly_growth)
        values.append(new_value)

    if annual_inflation != 0.0:
        values_real = [v / ((1 + monthly_inflation) ** m) for m, v in enumerate(values)]
    else:
        values_real = values

    df = pl.DataFrame(
        {
            "month": list(range(n_months + 1)),
            "year": [m // 12 for m in range(n_months + 1)],
            "house_value": values,
            "house_value_real": values_real,
        },
        schema={
            "month": pl.Int64,
            "year": pl.Int64,
            "house_value": pl.Float64,
            "house_value_real": pl.Float64,
        },
    )

    return df


def mortgage_monthly(
    loan_amount: float,
    annual_interest_rate: float,
    loan_term_years: int,
    annual_inflation: float = 0.0,
) -> pl.DataFrame:
    n_months = loan_term_years * 12
    r_monthly = annual_interest_rate / 12.0
    i_monthly = (1 + annual_inflation) ** (1 / 12) - 1 if annual_inflation != 0 else 0.0

    # fixed monthly payment formula
    if r_monthly > 0:
        monthly_payment = (
            loan_amount
            * r_monthly
            * (1 + r_monthly) ** n_months
            / ((1 + r_monthly) ** n_months - 1)
        )
    else:
        monthly_payment = loan_amount / n_months

    balance = [loan_amount]
    cumulative_principal = [0.0]
    cumulative_interest = [0.0]

    for m in range(1, n_months + 1):
        interest = balance[-1] * r_monthly
        principal_paid = monthly_payment - interest
        new_balance = balance[-1] - principal_paid

        balance.append(new_balance)
        cumulative_principal.append(cumulative_principal[-1] + principal_paid)
        cumulative_interest.append(cumulative_interest[-1] + interest)

    if annual_inflation != 0.0:
        balance_real = [b / ((1 + i_monthly) ** m) for m, b in enumerate(balance)]
        cumulative_principal_real = [
            p / ((1 + i_monthly) ** m) for m, p in enumerate(cumulative_principal)
        ]
        cumulative_interest_real = [
            i / ((1 + i_monthly) ** m) for m, i in enumerate(cumulative_interest)
        ]
    else:
        balance_real = balance
        cumulative_principal_real = cumulative_principal
        cumulative_interest_real = cumulative_interest

    df = pl.DataFrame(
        {
            "month": list(range(n_months + 1)),
            "year": [m // 12 for m in range(n_months + 1)],
            "monthly_payment": [monthly_payment] * (n_months + 1),
            "remaining_balance": balance,
            "remaining_balance_real": balance_real,
            "cumulative_principal": cumulative_principal,
            "cumulative_principal_real": cumulative_principal_real,
            "cumulative_interest": cumulative_interest,
            "cumulative_interest_real": cumulative_interest_real,
        },
        schema={
            "month": pl.Int64,
            "year": pl.Int64,
            "monthly_payment": pl.Float64,
            "remaining_balance": pl.Float64,
            "remaining_balance_real": pl.Float64,
            "cumulative_principal": pl.Float64,
            "cumulative_principal_real": pl.Float64,
            "cumulative_interest": pl.Float64,
            "cumulative_interest_real": pl.Float64,
        },
    )

    return df


def house_equity_over_time(
    initial_price: float,
    annual_value_change: float,
    loan_amount: float,
    annual_interest_rate: float,
    loan_term_years: int,
    years: int,
    annual_inflation: float = 0.0,
) -> pl.DataFrame:
    # get monthly house values and mortgage schedule
    house_df = house_value_monthly(
        initial_price, annual_value_change, years, annual_inflation
    )
    mortgage_df = mortgage_monthly(
        loan_amount, annual_interest_rate, loan_term_years, annual_inflation
    )

    # join on month
    df = house_df.join(mortgage_df, on="month", how="left")

    # compute equity
    df = df.with_columns(
        [
            (pl.col("house_value") - pl.col("remaining_balance")).alias("equity"),
            (pl.col("house_value_real") - pl.col("remaining_balance_real")).alias(
                "equity_real"
            ),
        ]
    )

    return df
