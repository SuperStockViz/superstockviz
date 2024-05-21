# Imports
# Standard Library Imports
from __future__ import annotations
import datetime

# External Imports
import numpy as np
import pandas as pd
import streamlit as st

# Local Imports
import sviz

# Setup/Data Reading

# Read in stock data
stock_df = pd.read_csv("./data/stockprice.csv", header=[0,1], index_col=0)
sp500info_df = pd.read_csv("./data/sp500info.csv", index_col=0)

# Process data
stock_df_list = []

for attr in np.unique(stock_df.columns.get_level_values(0)):
    stock_df_list.append(stock_df[attr].reset_index().melt(id_vars=["Date"], var_name = "ticker", value_name=attr).set_index(["Date", "ticker"]))

stock_data = pd.concat(stock_df_list, axis=1).reset_index().merge(sp500info_df, how="inner", left_on="ticker", right_on="Symbol")
stock_data["Date"] = pd.to_datetime(stock_data["Date"], format="%Y-%m-%d").dt.date



# Start of Page
st.header("Welcome to SuperStockViz!")
# Input list of tickers, can be seperated in any way
ticker_str = st.text_input("Enter tickers")
# Parse tickers
ticker_list = sviz.parse_tickers(ticker_str=ticker_str)


if len(ticker_list) == 1 and ticker_list[0]=="SP500":
    industries = list(np.unique(stock_data["GICS Sector"]))
else:
    industries = list(np.unique(stock_data[stock_data["ticker"].isin(ticker_list)]["GICS Sector"]))
industries.sort()
industry_options = ["All"] + industries


industry_filter = st.selectbox("Filter by Sector", industry_options)
if industry_filter == "All":
    industry_filter = industries
else:
    industry_filter = [industry_filter]

# Date Filter
start_date = datetime.date(2014,1,1)
end_date = datetime.date(2023, 12,31)

date_tuple = st.date_input(
    "Choose your Date Range of Interest",
    (start_date, end_date),
    min_value=start_date, 
    max_value=end_date,
    format="YYYY-MM-DD" 
)

if len(date_tuple)!=2:
    date_tuple = (start_date, end_date)

start, end = date_tuple

type(start)





# Display Altair Chart
st.altair_chart(sviz.stock_chart(stock_data=stock_data[
    (stock_data["Date"]>=start)&(stock_data["Date"]<=end)
    ][stock_data["GICS Sector"].isin(industry_filter)], 
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
                                 aggregate_func="mean"))