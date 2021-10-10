import pandas as pd
import yfinance as yf
from yahoofinancials import YahooFinancials
import numpy as np

def getStockData():
    ticker = yf.Ticker('TSLA')
    tsla_df = ticker.history(period="max")
    stockData = tsla_df['Close']
    return np.array(stockData)