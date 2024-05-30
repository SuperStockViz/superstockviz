# Imports
# Standard Library Imports
from datetime import date

# External Imports
import ibis
import pandas as pd
import streamlit as st

# Local Imports
import sviz

# Page config
st.set_page_config(layout="wide")

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

# Connect to motherduck database, and cache the connection
@st.cache_resource
def get_database_connection():
    md_token = st.secrets["MOTHERDUCK_TOKEN"]
    return ibis.duckdb.connect(f"md:?motherduck_token={md_token}")

stock_prices = get_database_connection().table("stock_prices")

if 'sp500info_df' not in st.session_state:
    sp500info_df = pd.read_csv("./data/sp500info.csv", index_col=0)
    possible_tickers = sp500info_df["Symbol"].sort_values(ascending=True)

if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False



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
    st.session_state.form_submitted = True
    

st.button('Submit', on_click=read_form)

with st.expander("See More Information on Companies"):
    st.dataframe(sp500info_df.rename({"Symbol":"Ticker"}, axis=1))


def display_backtest_chart(container):
    if len(st.session_state.data)<1:
        return None
    t = st.session_state.data["ticker"].iloc[0]
    start_date = st.session_state.data["start_date"].iloc[0]
    end_date = st.session_state.data["end_date"].iloc[0]
    selection = (stock_prices.ticker==t)&(stock_prices.Date>=start_date)&(stock_prices.Date<=end_date)
    for i in range(1, len(st.session_state.data)):
        t = st.session_state.data.iloc[i]["ticker"]
        start_date = st.session_state.data.iloc[i]["start_date"]
        end_date = st.session_state.data.iloc[i]["end_date"]
        selection = selection | ((stock_prices.ticker==t)&
                                 (stock_prices.Date>=start_date)&
                                 (stock_prices.Date<=end_date))
    stock_df = stock_prices.filter(selection).to_pandas()
    stock_df["Date"] = pd.to_datetime(stock_df["Date"], format="%Y-%m-%d").dt.date
    gains_chart = sviz.backtest(stock_choice=st.session_state.data, 
                              stock_df=stock_df, 
                              width=650,
                              upper_height=300, 
                              lower_height=150,
                              #adjust_inflation = adjust_inflation,
                              price="Close")
    container.altair_chart(gains_chart,use_container_width=True)
    st.session_state.form_submitted = False

c=st.empty()

if st.session_state.form_submitted:
    display_backtest_chart(c)

st.markdown(
    """
    ## Data Sources:  
    [Yahoo Finance](https://finance.yahoo.com): Stock prices  
    [yfinance](https://pypi.org/project/yfinance/): Used to get stock price data from Yahoo Finanace  
    [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies): Information on SP500 companies  
    [GNews](https://github.com/ranahaani/GNews): Used to get news stories from Google News  
    """
)