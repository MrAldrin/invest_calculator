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
    tax_rate: float = 0.3784,  # 37.84% tax on returns
) -> pl.DataFrame:
    n_months = years * 12
    monthly_return = (1 + annual_return) ** (1 / 12) - 1
    # .3784 # tax on returns
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
    df = df.with_columns(
        [
            (pl.col("returns_cum") * (1 - tax_rate)).alias("returns_after_tax"),
            (
                pl.col("contributions_cum") + pl.col("returns_cum") * (1 - tax_rate)
            ).alias("stock_equity"),
        ]
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


def property_value_monthly(
    initial_price: float,
    annual_value_change: float,
    time_horizon_years: int,
    annual_inflation: float = 0.0,
) -> pl.DataFrame:
    n_months = time_horizon_years * 12
    monthly_growth = (1 + annual_value_change) ** (1 / 12) - 1

    values = [initial_price]
    for m in range(1, n_months + 1):
        new_value = values[-1] * (1 + monthly_growth)
        values.append(new_value)

    df = pl.DataFrame(
        {
            "month": list(range(n_months + 1)),
            "year": [m // 12 for m in range(n_months + 1)],
            "property_value": values,
        },
        schema={
            "month": pl.Int64,
            "year": pl.Int64,
            "property_value": pl.Float64,
        },
    )

    df = apply_inflation(df, annual_inflation, ["property_value"])

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

    loan_payment = (
        loan_amount
        * r_monthly
        * (1 + r_monthly) ** n_months
        / ((1 + r_monthly) ** n_months - 1)
    )

    balance = [loan_amount]
    interest = [0.0]  # Interest paid each month
    tax_deductions = [0.0]  # Tax savings each month
    net_costs = [0.0]  # Net cost after tax savings
    principal_cum = [0.0]
    interest_cum = [0.0]

    for m in range(1, n_months + 1):
        interest_payment = balance[-1] * r_monthly
        principal_payment = loan_payment - interest_payment
        new_balance = max(0, balance[-1] - principal_payment)

        tax_deduction = interest_payment * 0.22 if rentefradrag else 0.0
        net_cost = loan_payment - tax_deduction

        balance.append(new_balance)
        interest.append(interest_payment)
        tax_deductions.append(tax_deduction)
        net_costs.append(net_cost)
        principal_cum.append(principal_cum[-1] + principal_payment)
        interest_cum.append(interest_cum[-1] + interest_payment)

    df = pl.DataFrame(
        {
            "month": list(range(n_months + 1)),
            "year": [m // 12 for m in range(n_months + 1)],
            "loan_payment": [0.0] + [loan_payment] * n_months,
            "interest": interest,
            "tax_deduction": tax_deductions,
            "net_cost": net_costs,  # What it actually costs you
            "loan_balance": balance,
            "principal_cum": principal_cum,
            "interest_cum": interest_cum,
        },
        schema={
            "month": pl.Int64,
            "year": pl.Int64,
            "loan_payment": pl.Float64,
            "interest": pl.Float64,
            "tax_deduction": pl.Float64,
            "net_cost": pl.Float64,
            "loan_balance": pl.Float64,
            "principal_cum": pl.Float64,
            "interest_cum": pl.Float64,
        },
    )

    df = apply_inflation(
        df,
        annual_inflation,
        [
            "loan_payment",
            "interest",
            "tax_deduction",
            "net_cost",
            "loan_balance",
            "principal_cum",
            "interest_cum",
        ],
    )

    return df


def property_equity_over_time(
    initial_price: float,
    annual_value_change: float,
    loan_amount: float,
    annual_interest_rate: float,
    loan_term_years: int,
    time_horizon_years: int,
    annual_inflation: float = 0.0,
    rentefradrag: bool = True,
) -> pl.DataFrame:
    # get monthly house values and mortgage schedule
    property_df = property_value_monthly(
        initial_price, annual_value_change, time_horizon_years, annual_inflation
    )
    mortgage_df = mortgage_monthly(
        loan_amount,
        annual_interest_rate,
        loan_term_years,
        annual_inflation,
        rentefradrag=rentefradrag,
    )

    # join on month
    df = property_df.join(mortgage_df, on=["month", "year"], how="left")

    df = df.with_columns(
        [
            pl.col("loan_payment").fill_null(0.0),
            pl.col("loan_balance").fill_null(0.0),
            pl.col("principal_cum").fill_null(strategy="forward"),
            pl.col("interest_cum").fill_null(strategy="forward"),
        ]
    )
    # compute equity
    df = df.with_columns(
        [
            (pl.col("property_value") - pl.col("loan_balance")).alias(
                "property_equity"
            ),
        ]
    )

    return df


def combined_property_and_stocks(
    property_price: float,
    annual_property_appreciation: float,
    loan_amount: float,
    annual_interest_rate: float,
    loan_term_years: int,
    initial_stock_investment: float,
    monthly_stock_investment: float,
    annual_stock_return: float,
    time_horizon_years: int,
    annual_inflation: float = 0.0,
    rentefradrag: bool = True,
) -> pl.DataFrame:
    """
    Combines house equity growth with stock investment returns.
    Returns a DataFrame with both house equity and stock portfolio values.
    """
    # Get house equity over time
    property_df = property_equity_over_time(
        property_price,
        annual_property_appreciation,
        loan_amount,
        annual_interest_rate,
        loan_term_years,
        time_horizon_years,
        annual_inflation,
        rentefradrag=rentefradrag,
    )

    # Get stock investment over time
    stock_df = stock_investment_monthly(
        initial_investment=initial_stock_investment,
        monthly_contribution=monthly_stock_investment,
        annual_return=annual_stock_return,
        years=time_horizon_years,
        annual_inflation=annual_inflation,
    )

    # Combine the data
    combined_df = property_df.join(stock_df, on=["month", "year"], how="left")

    # Rename stock columns to avoid confusion
    combined_df = combined_df.rename(
        {
            "balance": "stock_balance",
            "contributions_cum": "stock_buy_price",
            "returns_cum": "stock_returns",
        }
    )

    # Calculate total net worth
    combined_df = combined_df.with_columns(
        (pl.col("property_equity") + pl.col("stock_equity")).alias("total_net_worth"),
    )

    return combined_df
