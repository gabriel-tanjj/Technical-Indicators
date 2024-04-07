import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

tickers = ["AAPL", "GOOG", "MSFT", "AMZN", "COIN"]

ohlcv_data = {}

for stock in tickers:
    data = yf.download(stock, period="max")
    data.dropna(inplace=True)
    ohlcv_data[stock] = data

def macd(df, short, long, signal):
    df = df.copy()
    df["MA_Fast"] = df["Adj Close"].ewm(span=short, min_periods=short).mean()
    df["MA_Slow"] = df["Adj Close"].ewm(span=long, min_periods=long).mean()
    df["MACD"] = df["MA_Fast"] - df["MA_Slow"]
    df["Signal"] = df["MACD"].ewm(span=signal, min_periods=signal).mean()
    return df.loc[:, ["MACD", "Signal"]]

for ticker in ohlcv_data:
    ohlcv_data[ticker][["MACD", "Signal"]] = macd(df=ohlcv_data[ticker], short=12, long=26, signal =9)


for ticker in ohlcv_data:
    ohlcv_data[ticker][["Adj Close", "MACD", "Signal"]].plot(figsize=(20,12))
    plt.title(f"{ticker} + MACD")
    plt.show()

