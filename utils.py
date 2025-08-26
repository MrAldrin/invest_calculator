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

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
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
            "balance": [float(b) for b in balance],
            "contributions_cum": [float(c) for c in contributions_cum],
            "returns_cum": [float(r) for r in returns_cum],
        }
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
        }
    )

    return df
