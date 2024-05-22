# Imports
# Standard Library Imports
from __future__ import annotations
import re

# External Imports

# Local Imports

TICKER_REGEX = re.compile(r"[A-Za-z]+[0-9]*")

def parse_tickers(ticker_str:str)->list[str]:
    """Parse a string of tickers into a list

    Args:
        ticker_str (str): String list of tickers to parse

    Returns:
        list[str]: Parsed list of tickers
    """
    return [x.upper() for x in TICKER_REGEX.findall(ticker_str)]