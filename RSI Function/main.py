import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

tickers = ["EURUSD=X", "GBPJPY=X"]
ohlcv_data = {}

# Loop over tickers and store data in the OHLCV dataframe in the dictionary
for ticker in tickers:
    temp_df = yf.download(ticker, period="1mo", interval="15m")
    temp_df.dropna(inplace=True)
    ohlcv_data[ticker] = temp_df

def ATR(DF, len=14):
    # Copy function used so we don't change the original dataset
    df = DF.copy()
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Adj Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Adj Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].ewm(min_periods=len, span=len).mean()
    return df["ATR"]

for ticker in tickers:
    ohlcv_data[ticker]["ATR"] = ATR(ohlcv_data[ticker])

print(ohlcv_data["EURUSD=X"])