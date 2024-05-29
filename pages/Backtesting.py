# Imports
# Standard Library Imports
from datetime import date

# External Imports
import pandas as pd
import streamlit as st

# Local Imports
import sviz

# Title
st.write('# Backtesting')
st.markdown(
    """
    Test out how your investments would have done with past data! Choose a number of stocks to 
    invest, and the table will update allowing you to enter information for those different 
    stocks. Choose companies to invest in by ticker (information on different companies can be found
    by clicking on the 'See More Information on Companies'), then choose an amount and when you would like to 
    buy and sell the stock. Finally click submit and see how well your stock choices would have done! 

    The generated chart includes tooltips so you can see specific prices on different dates, and 
    by you can examine different date ranges by selecting them on the bottom chart.  
    """
)

# Create empty dataframe to hold form input
if 'data' not in st.session_state:
    data = pd.DataFrame({'ticker':[],'invest_amount':[],'start_date':[],'end_date':[]})
    st.session_state.data = data

if 'stock_df' not in st.session_state:
    stock_df = pd.read_csv("./data/stockprice.csv", header=[0,1], index_col=0)
    possible_tickers = stock_df["Close"].columns
    stock_df.index = pd.to_datetime(stock_df.index, format = "%Y-%m-%d").date
    sp500info_df = pd.read_csv("./data/sp500info.csv", index_col=0)


# Show Dataframe (For testing)
# st.dataframe(st.session_state.data)



# a selection for the user to specify the number of rows
num_rows = st.slider('Number of Stocks', min_value=1, max_value=10)

# a selection for user to specify if value should be inflation adjusted
#adjust_inflation = st.checkbox("Adjust for Inflation")

# columns to lay out the inputs
grid = st.columns(4)

# Start and End dates Allowed for backtesting
BEGIN_DATE = date(2014, 1, 1)
END_DATE = date(2023, 12, 31)


# Function to create a row of widgets (with row number input to assure unique keys)
def add_row(row):
    with grid[0]:
        st.selectbox('Ticker', possible_tickers, key=f'ticker{row}')
    with grid[1]:
        st.number_input('Amount to Invest', step=100, key=f'invest_amount{row}')
    with grid[2]:
        st.date_input('Start Date', BEGIN_DATE, 
                      min_value=BEGIN_DATE, 
                      max_value=END_DATE, 
                      key = f"start_date{row}", 
                      format="MM/DD/YYYY")
    with grid[3]:
        st.date_input('End Date', END_DATE, 
                      min_value=BEGIN_DATE, 
                      max_value=END_DATE, 
                      key = f"end_date{row}", 
                      format="MM/DD/YYYY")

for r in range(num_rows):
    add_row(r)

def read_form():
    data = pd.DataFrame({'ticker':[],'invest_amount':[],'start_date':[],'end_date':[]})
    st.session_state.data = data
    for row in range(num_rows):
        r = pd.DataFrame({'ticker':[st.session_state[f"ticker{row}"].upper()],
                'invest_amount':[st.session_state[f"invest_amount{row}"]],
                'start_date':[st.session_state[f"start_date{row}"]],
                'end_date':[st.session_state[f'end_date{row}']]})
        st.session_state.data = pd.concat([st.session_state.data, r])

st.button('Submit', on_click=read_form)

with st.expander("See More Information on Companies"):
    st.dataframe(sp500info_df.rename({"Symbol":"Ticker"}, axis=1))


if len(st.session_state.data) > 0:
    gains_chart = sviz.backtest(stock_choice=st.session_state.data, 
                              stock_df=stock_df, 
                              width=650,
                              upper_height=300, 
                              lower_height=150,
                              #adjust_inflation = adjust_inflation,
                              price="Close")
    st.altair_chart(gains_chart)

st.markdown(
    """
    ## Data Sources:  
    [Yahoo Finance](https://finance.yahoo.com): Stock prices  
    [yfinance](https://pypi.org/project/yfinance/): Used to get stock price data from Yahoo Finanace  
    [CPI](https://palewi.re/docs/cpi/): Inflation adjustment  
    [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies): Information on SP500 companies  
    [GNews](https://github.com/ranahaani/GNews): Used to get news stories from Google News  
    """
)