import pandas as pd
import yfinance as yf
from yahoofinancials import YahooFinancials
import numpy as np

def getStockData():
    ticker = yf.Ticker('XRP-USD')
    df = ticker.history(period="max") #https://yahooquery.dpguthrie.com/guide/ticker/historical/
    #stockData = df['Close']
    return df