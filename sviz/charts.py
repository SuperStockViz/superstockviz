# Imports
# Standard Library Imports
from __future__ import annotations

# External Imports
import altair as alt
import pandas as pd

# Local Imports

# Setup vegafusion
alt.data_transformers.enable("vegafusion")


# region Wrapper Function


def stock_chart(
    stock_data: pd.DataFrame,
    tickers: list[str],
    width: int | float = 650,
    upper_height: int | float = 650,
    lower_height: int | float = 100,
    date_col: str = "Date",
    ticker_col: str = "ticker",
    price_col: str = "Close",
    open_col: str = "Open",
    close_col: str = "Close",
    high_col: str = "High",
    low_col: str = "Low",
    aggregate_func: str = "mean"
)-> alt.Chart:
    if len(tickers) == 1:
        ticker = tickers[0]
        if ticker == "SP500" or ticker == "FULL":
            return aggregate_company(
                stock_data=stock_data,
                width=width,
                upper_height=upper_height,
                lower_height=lower_height,
                date_col=date_col,
                price_col=price_col,
            )
        return candlestick(
            stock_data=stock_data[stock_data[ticker_col] == ticker],
            width=width,
            upper_height=upper_height,
            lower_height=lower_height,
            date_col=date_col,
            open_col=open_col,
            close_col=close_col,
            high_col=high_col,
            low_col=low_col,
        )
    if 2 <= len(tickers) <= 5:
        return multiple_company(
            stock_data=stock_data[stock_data[ticker_col].isin(tickers)],
            width=width,
            upper_height=upper_height,
            lower_height=lower_height,
            date_col=date_col,
            price_col=price_col,
            ticker_col=ticker_col,
        )
    return aggregate_company(
        stock_data=stock_data,
        width=width,
        upper_height=upper_height,
        lower_height=lower_height,
        date_col=date_col,
        price_col=price_col,
        aggregate_func=aggregate_func
    )


# endregion Wrapper Function


# region Individual Charting Functions


def candlestick(
    stock_data: pd.DataFrame,
    width: int | float = 650,
    upper_height: int | float = 650,
    lower_height: int | float = 100,
    date_col: str = "Date",
    open_col: str = "Open",
    close_col: str = "Close",
    high_col: str = "High",
    low_col: str = "Low",
):
    """Create a candlestick chart for stock data using altair

    Args:
        stock_data (pd.DataFrame): Stock data
        width (int|float): Width of the chart
        upper_height (int|float): Height of candlestick chart
        lower_height (int|float): Height of time selector
        date_col (str): Name of column containing the date
        open_col (str): Name of column containing the open price
        close_col (str): Name of column constaining the close price
        high_col (str): Name of column containing the high price
        low_col (str): Name of column containing the low price

    Returns:
        alt.Chart: Candlestick chart with full year brush
    """
    # Time series stock chart
    # Time brush
    time_brush = alt.selection_interval(encodings=["x"])

    # Set color for rising or falling price
    open_close_color = alt.condition(
        f"datum.{open_col} <= datum.{close_col}",
        alt.value("#06982d"),
        alt.value("#ae1325"),
    )

    # Base chart
    base = (
        alt.Chart(stock_data)
        .encode(
            alt.X(f"{date_col}:T", scale=alt.Scale(domain=time_brush))
            .axis(format="%Y-%m-%d")
            .title("Date"),
            color=open_close_color,
        )
        .properties(width=width, height=upper_height)
    )

    rule = base.mark_rule().encode(
        alt.Y(f"{low_col}:Q").title("Price (USD)").scale(zero=False),
        alt.Y2(f"{high_col}:Q"),
    )

    bar = base.mark_bar().encode(alt.Y("Open:Q").scale(zero=False), alt.Y2("Close:Q"))

    # Full year selector
    full_year = (
        alt.Chart(stock_data)
        .mark_line()
        .add_params(time_brush)
        .encode(alt.X("Date:T"), alt.Y(f"{close_col}", title="Close (USD)"))
        .properties(width=width, height=lower_height)
    )

    return alt.vconcat(rule + bar, full_year)


def multiple_company(
    stock_data: pd.DataFrame,
    width: int | float = 650,
    upper_height: int | float = 650,
    lower_height: int | float = 100,
    date_col: str = "Date",
    price_col: str = "Open",
    ticker_col: str = "ticker",
):
    """Create a candlestick chart for stock data using altair

    Args:
        stock_data (pd.DataFrame): Stock data
        width (int|float): Width of the chart
        upper_height (int|float): Height of candlestick chart
        lower_height (int|float): Height of time selector
        date (str): Name of column containing the date
        price_col (str): Name of column containing the price
        ticker_col (str): Name of column constaining the tickers

    Returns:
        alt.Chart: Line chart with companies differentiated by color,
            and time selection chart below
    """
    # Time series stock chart
    # Time brush
    time_brush = alt.selection_interval(encodings=["x"])

    base_chart = (
        alt.Chart(stock_data)
        .mark_line()
        .encode(
            alt.Y(f"{price_col}:Q", title="Price"),
            alt.Color(f"{ticker_col}:N", title="Ticker"),
        )
    )

    stock_chart = base_chart.encode(
        alt.X(f"{date_col}:T", scale=alt.Scale(domain=time_brush), title="Date")
    ).properties(width=width, height=upper_height)

    # time chart selector
    time_chart = (
        base_chart.add_params(time_brush)
        .encode(alt.X(f"{date_col}:T"))
        .properties(width=width, height=lower_height)
    )

    return alt.vconcat(stock_chart, time_chart)


def aggregate_company(
    stock_data: pd.DataFrame,
    width: int | float = 650,
    upper_height: int | float = 650,
    lower_height: int | float = 100,
    date_col: str = "Date",
    price_col: str = "Open",
    ticker_col: str = "ticker",
    aggregate_func: str = "mean",
):
    """Create a candlestick chart for stock data using altair

    Args:
        stock_data (pd.DataFrame): Stock data
        width (int|float): Width of the chart
        upper_height (int|float): Height of candlestick chart
        lower_height (int|float): Height of time selector
        date (str): Name of column containing the date
        price_col (str): Name of column containing the price
        ticker_col (str): Name of column constaining the tickers
        aggregate_func (str): String describing function to use for
            aggregation, like median, mean, etc.

    Returns:
        alt.Chart: Line chart with companies aggregated,
            and time selection chart below
    """
    # Time series stock chart
    # Time brush
    time_brush = alt.selection_interval(encodings=["x"])

    base_chart = (
        alt.Chart(stock_data)
        .mark_line()
        .encode(alt.Y(f"{aggregate_func}({price_col}):Q", title="Average Price"))
    )

    stock_chart = base_chart.encode(
        alt.X(f"{date_col}:T", scale=alt.Scale(domain=time_brush), title="Date")
    ).properties(width=width, height=upper_height)

    # time chart selector
    time_chart = (
        base_chart.add_params(time_brush)
        .encode(alt.X(f"{date_col}:T"))
        .properties(width=width, height=lower_height)
    )

    return alt.vconcat(stock_chart, time_chart)


# endregion Individual Charting Functions
