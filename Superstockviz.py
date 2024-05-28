# Imports
# Standard Library Imports
from __future__ import annotations
import datetime
import os

# External Imports
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Local Imports
import sviz

# Setup/Data Reading
# Streamlit setup
st.set_page_config(layout="wide")

# Read in stock data if not already read in
if "stock_df" not in st.session_state:
    stock_df = pd.read_csv("./data/stockprice.csv", header=[0, 1], index_col=0)
    possible_tickers = stock_df["Close"].columns
    sp500info_df = pd.read_csv("./data/sp500info.csv", index_col=0)

    # Process data
    stock_df_list = []

    for attr in np.unique(stock_df.columns.get_level_values(0)):
        stock_df_list.append(
            stock_df[attr]
            .reset_index()
            .melt(id_vars=["Date"], var_name="ticker", value_name=attr)
            .set_index(["Date", "ticker"])
        )

    stock_data = (
        pd.concat(stock_df_list, axis=1)
        .reset_index()
        .merge(sp500info_df, how="inner", left_on="ticker", right_on="Symbol")
    )
    stock_data["Date"] = pd.to_datetime(stock_data["Date"], format="%Y-%m-%d").dt.date

    stock_data["median"] = (stock_data["Open"]+stock_data["Close"])/2

    news_data = pd.read_csv("./data/top_news.csv", index_col=0)
    news_data["Date"] = pd.to_datetime(news_data["Date"], format="%Y-%m-%d").dt.date

    stock_data = stock_data.merge(news_data, on=["Date", "ticker"], how="left")

# Determine which annotations are available
annotated_tickers = [x.split(".")[0] for x in os.listdir("./data/news_annotated")]

# Start of Page
st.header("Welcome to SuperStockViz!")


st.header("Adaptive Stock Viewer")

# Input Form
ticker_list = st.multiselect("Enter tickers of interest", possible_tickers)
with st.expander("See More Information on Companies"):
    st.dataframe(sp500info_df.rename({"Symbol": "Ticker"}, axis=1))


if len(ticker_list) == 1 and ticker_list[0] == "SP500":
    industries = list(np.unique(stock_data["GICS Sector"]))
else:
    industries = list(
        np.unique(stock_data[stock_data["ticker"].isin(ticker_list)]["GICS Sector"])
    )
industries.sort()
industry_options = ["All"] + industries

# Date Filter
start_date = datetime.date(2014, 1, 1)
end_date = datetime.date(2023, 12, 31)

date_tuple = st.date_input(
    "Choose your Date Range of Interest",
    (start_date, end_date),
    min_value=start_date,
    max_value=end_date,
    format="YYYY-MM-DD",
)

if len(date_tuple) != 2:
    date_tuple = (start_date, end_date)

start, end = date_tuple

industry_filter = st.selectbox("Filter by Sector", industry_options)
if industry_filter == "All":
    industry_filter = industries
else:
    industry_filter = [industry_filter]

# Display Altair Chart
if len(ticker_list) > 0:
    stock_df = stock_data[(stock_data["Date"] >= start) & (stock_data["Date"] <= end)][
        stock_data["GICS Sector"].isin(industry_filter)
    ]
    st.altair_chart(
        sviz.stock_chart(
            stock_data=stock_df,
            tickers=ticker_list,
            width=650,
            upper_height=300,
            lower_height=100,
            date_col="Date",
            ticker_col="ticker",
            price_col="Close",
            open_col="Open",
            close_col="Close",
            high_col="High",
            low_col="Low",
            aggregate_func="mean",
        ),
        use_container_width=True,
    )


st.header("Annotated Stock Price Data")

annotated_ticker = st.selectbox(
    "Select a Ticker of Interest", [x.split(".")[0] for x in annotated_tickers]
)
with open(f"./data/news_annotated/{annotated_ticker}.html", "r") as f:
    annotated_news_chart = f.read()
components.html(annotated_news_chart, height=800, width=1000)
