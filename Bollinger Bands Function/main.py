import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

tickers = ["EURUSD=X", "GBPJPY=X", "AMZN", "MSFT", "GOOG"]
ohlcv_data = {}

for ticker in tickers:
    temp_df = yf.download(ticker, period="1mo", interval="15m")
    temp_df.dropna(inplace=True)
    ohlcv_data[ticker] = temp_df

def bb(df, len=20):
    df = df.copy()
    df["Mid Band"] = df["Adj Close"].rolling(len).mean()
    # ddof=0 is for calculating the population standard deviation (n) not n-1 (sample)
    df["Upper Band"] = df["Mid Band"] + 2 * df["Adj Close"].rolling(len).std(ddof=0)
    df["Lower Band"] = df["Mid Band"] - 2 * df["Adj Close"].rolling(len).std(ddof=0)
    df["BB Width"] = df["Upper Band"] - df["Lower Band"]
    return df[["Mid Band", "Upper Band", "Lower Band", "BB Width"]]

for ticker in tickers:
    ohlcv_data[ticker][["Mid Band", "Upper Band", "Lower Band", "BB Width"]] = bb(ohlcv_data[ticker])

print(ohlcv_data["EURUSD=X"].tail())

for ticker in tickers:
    ohlcv_data[ticker][["Adj Close", "Mid Band", "Upper Band", "Lower Band"]].plot()
    plt.title("BB for {}".format(ticker))
    plt.show()
