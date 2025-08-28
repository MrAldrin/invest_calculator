import polars as pl


def apply_inflation(
    df: pl.DataFrame, annual_inflation: float, columns: list[str]
) -> pl.DataFrame:
    monthly_inflation = (1 + annual_inflation) ** (1 / 12) - 1
    df = df.with_columns(
        [
            (pl.col(col) / ((1 + monthly_inflation) ** pl.arange(0, pl.len())))
            for col in columns
        ]
    )
    return df


def stock_investment_monthly(
    initial_investment: float,
    monthly_contribution: float,
    annual_return: float,
    years: int,
    annual_inflation: float = 0.0,
) -> pl.DataFrame:
    n_months = years * 12
    monthly_return = (1 + annual_return) ** (1 / 12) - 1

    balance = [initial_investment]
    contributions_cum = [initial_investment]
    returns_cum = [0.0]

    for m in range(1, n_months + 1):
        # previous balance grows
        interest = balance[-1] * monthly_return
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

    df = apply_inflation(
        df, annual_inflation, ["balance", "contributions_cum", "returns_cum"]
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

    values = [initial_price]
    for m in range(1, n_months + 1):
        new_value = values[-1] * (1 + monthly_growth)
        values.append(new_value)

    df = pl.DataFrame(
        {
            "month": list(range(n_months + 1)),
            "year": [m // 12 for m in range(n_months + 1)],
            "house_value": values,
        },
        schema={
            "month": pl.Int64,
            "year": pl.Int64,
            "house_value": pl.Float64,
        },
    )

    df = apply_inflation(df, annual_inflation, ["house_value"])

    return df


def mortgage_monthly(
    loan_amount: float,
    annual_interest_rate: float,
    loan_term_years: int,
    annual_inflation: float = 0.0,
    rentefradrag: bool = True,
) -> pl.DataFrame:
    n_months = loan_term_years * 12
    r_monthly = annual_interest_rate / 12.0

    if rentefradrag:
        r_monthly *= 0.78

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

    df = pl.DataFrame(
        {
            "month": list(range(n_months + 1)),
            "year": [m // 12 for m in range(n_months + 1)],
            "monthly_payment": [monthly_payment] * (n_months + 1),
            "remaining_balance": balance,
            "cumulative_principal": cumulative_principal,
            "cumulative_interest": cumulative_interest,
        },
        schema={
            "month": pl.Int64,
            "year": pl.Int64,
            "monthly_payment": pl.Float64,
            "remaining_balance": pl.Float64,
            "cumulative_principal": pl.Float64,
            "cumulative_interest": pl.Float64,
        },
    )

    df = apply_inflation(
        df,
        annual_inflation,
        ["remaining_balance", "cumulative_principal", "cumulative_interest"],
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
    rentefradrag: bool = True,
) -> pl.DataFrame:
    # get monthly house values and mortgage schedule
    house_df = house_value_monthly(
        initial_price, annual_value_change, years, annual_inflation
    )
    mortgage_df = mortgage_monthly(
        loan_amount,
        annual_interest_rate,
        loan_term_years,
        annual_inflation,
        rentefradrag=rentefradrag,
    )

    # join on month
    df = house_df.join(mortgage_df, on=["month", "year"], how="left")

    df = df.with_columns(
        [
            pl.col("monthly_payment").fill_null(0.0),
            pl.col("remaining_balance").fill_null(0.0),
            pl.col("cumulative_principal").fill_null(strategy="forward"),
            pl.col("cumulative_interest").fill_null(strategy="forward"),
        ]
    )
    # compute equity
    df = df.with_columns(
        [
            (pl.col("house_value") - pl.col("remaining_balance")).alias("equity"),
        ]
    )

    return df
