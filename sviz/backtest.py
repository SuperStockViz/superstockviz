# Imports
# Standard Library Imports
from __future__ import annotations

# External Imports
import altair as alt
import pandas as pd

# Local Imports

# Setup vegafusion
alt.data_transformers.enable("vegafusion")


def backtest(
    stock_choice: pd.DataFrame,
    stock_df: pd.DataFrame,
    width: int | float = 650,
    upper_height: int | float = 650,
    lower_height: int | float = 100,
    price: str = "Close",
) -> alt.Chart:
    price_df = stock_df[price]
    ticker_gains_list = []
    if len(stock_choice)==0:
        return None
    for idx, row in stock_choice.iterrows():
        ticker = row["ticker"]
        if ticker not in price_df.columns:
            continue
        ticker_series = price_df.loc[row["start_date"] : row["end_date"], ticker]
        start_price = ticker_series.iloc[0]
        stock_amount = row["invest_amount"] / start_price
        ticker_series = ticker_series * stock_amount
        ticker_series = ticker_series - ticker_series.iloc[0]
        ticker_series.name = ticker
        ticker_gains_list.append(ticker_series)
    total_gains = (
        pd.concat(ticker_gains_list, axis=1, ignore_index=False)
        .ffill(axis=0, limit=None, limit_area=None)
        .fillna(value=0.0)
    )
    total_gains["Total"] = total_gains.sum(axis=1)
    total_gain = total_gains["Total"].iloc[-1]

    total_gains = total_gains.reset_index(names="date")

    total_gains = pd.melt(
        total_gains, id_vars="date", var_name="ticker", value_name="gains"
    )

    time_brush = alt.selection_interval(encodings=["x"])

    title = alt.TitleParams('Total Gained: ${:,.2f}'.format(total_gain), anchor='middle')

    gains_chart = alt.Chart(total_gains, title=title).mark_line().encode(
        alt.X("date:T", scale=alt.Scale(domain=time_brush), title="Date"),
        alt.Y("gains:Q", title="Gains (USD)"),
        alt.Color("ticker:N", title="Ticker"),
    ).properties(width=width, height=upper_height)

    time_chart = (
        alt.Chart(total_gains).mark_line().add_params(time_brush)
        .encode(
            alt.X("date:T"),
            alt.Y("gains:Q", title="Gains (USD)"),
            alt.Color("ticker:N", title="Ticker"),
        )
        .properties(width=width, height=lower_height)
    )

    return alt.vconcat(gains_chart, time_chart)
