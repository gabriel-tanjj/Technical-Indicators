from alpha_vantage.timeseries import TimeSeries
import pandas as pd

key_path = "0DMBR8SRK4GTSK46"
all_tickers = ["EURUSD", "MSFT", "TSLA", "BABA", "COIN", "AMZN", "GOOG", "EURJPY"]
ts = TimeSeries(key=key_path, output_format='pandas')
data = ts.get_daily(symbol="EURUSD", outputsize="full")[0]
data.columns = ["Open", "High", "Low", "Close", "Volume"]

close_prices = pd.DataFrame()

for ticker in all_tickers:
    data = ts.get_daily(symbol=ticker, outputsize="full")[0]
    data.columns = ["Open", "High", "Low", "Close", "Volume"]
    close_prices[ticker] = data["Close"]


print(close_prices)