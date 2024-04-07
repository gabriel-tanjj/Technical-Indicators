import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# MACD Parameters
ema_s = 5
ema_l = 10
signal_window = 9
# RSI Parameters
rsi_period = 9
overbought = 70
oversold = 30
trading_cost = 0.00007

desired_width = 320
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)
pd.set_option('display.max_columns',20)

# Get Data MACD
data = pd.read_csv("forex_pairs.csv", parse_dates=["Date"], index_col="Date")
data = data["EURUSD=X"].to_frame().dropna()
data.rename(columns={"EURUSD=X": "Close"}, inplace=True)
macd_df = data.copy()
macd_df["Returns"] = np.log(macd_df["Close"].div(macd_df["Close"].shift(1)))
macd_df["EMA-S"] = macd_df["Close"].ewm(span=ema_s, min_periods=ema_l).mean()
macd_df["EMA-L"] = macd_df["Close"].ewm(span=ema_l, min_periods=ema_l).mean()
macd_df["MACD"] = macd_df["EMA-S"] - macd_df["EMA-L"]
macd_df["Signal"] = macd_df["MACD"].ewm(span=signal_window, min_periods=signal_window).mean()

# MACD Strategy
macd_df["MACD_Position"] = np.where(macd_df["MACD"] > macd_df["Signal"], 1, -1)
macd_df["MACD_Trades"] = macd_df["MACD_Position"].diff().fillna(0).abs()
macd_df.dropna(inplace=True)
macd_df["MACD_Strategy_Return"] = macd_df["MACD_Position"].shift(1) * macd_df["Returns"]
macd_df["MACD_Strategy_Return_Net"] = macd_df["MACD_Strategy_Return"] - (macd_df["MACD_Trades"] * trading_cost)

# Cumulative MACD Returns
macd_df["CReturns"] = macd_df["Returns"].cumsum().apply(np.exp)
macd_df["CMACD_Strategy_Return"] = macd_df["MACD_Strategy_Return"].cumsum().apply(np.exp)
macd_df["CMACD_Strategy_Return_Net"] = macd_df["MACD_Strategy_Return_Net"].cumsum().apply(np.exp)
macd_df[["CReturns", "CMACD_Strategy_Return", "CMACD_Strategy_Return_Net"]].plot(figsize=(12,8), title="EURUSD MACD Strategy")
# plt.show()
# print(macd_df)

# RSI Data
rsi_df = data.copy()
rsi_df["Returns"] = np.log(rsi_df["Close"].div(rsi_df["Close"].shift(1)))
rsi_df["RSI_U"] = np.where(rsi_df["Close"].diff() > 0, rsi_df["Close"].diff(), 0)
rsi_df["RSI_D"] = np.where(rsi_df["Close"].diff() < 0, -rsi_df["Close"].diff(), 0)
rsi_df["RSI_MA_U"] = rsi_df["RSI_U"].rolling(window=rsi_period).mean()
rsi_df["RSI_MA_D"] = rsi_df["RSI_D"].rolling(window=rsi_period).mean()
rsi_df["RSI"] = 100 - (100 / (1 + rsi_df["RSI_MA_U"] / rsi_df["RSI_MA_D"]))
rsi_df.dropna(inplace=True)

rsi_df[["RSI"]].plot(figsize=(12,8), title="EURUSD RSI Indicator")
# plt.hlines(y=overbought, xmin=data.index[0], xmax=data.index[-1], label="RSI Upper", color="red")
# plt.hlines(y=oversold, xmin=data.index[0], xmax=data.index[-1], label="RSI Lower", color="green")
# plt.show()

# RSI Strategy
rsi_df["RSI_Position"] = np.where(rsi_df["RSI"] > overbought, -1, np.nan)
rsi_df["RSI_Position"] = np.where(rsi_df["RSI"] < oversold, 1, rsi_df["RSI_Position"])
rsi_df["RSI_Position"] = rsi_df["RSI_Position"].fillna(0)

rsi_df["RSI_Strategy"] = rsi_df["Returns"] * rsi_df["RSI_Position"].shift(1)
rsi_df["RSI_Trades"] = rsi_df["RSI_Position"].diff().abs()
rsi_df["RSI_Strategy_Net"] = rsi_df["RSI_Strategy"] - rsi_df["RSI_Trades"] * trading_cost

# Cumulative
rsi_df["CReturns"] = rsi_df["Returns"].cumsum().apply(np.exp)
rsi_df["CRSI_Strategy"] = rsi_df["RSI_Strategy"].cumsum().apply(np.exp)
rsi_df["CRSI_Strategy_Net"] = rsi_df["RSI_Strategy_Net"].cumsum().apply(np.exp)

rsi_df[["CReturns", "CRSI_Strategy", "CRSI_Strategy_Net"]].plot(figsize=(12, 8), title="EURUSD - RSI Strategy")
# plt.show()

# Combined Strategy
comb = macd_df.loc[:, ["Returns", "MACD_Position"]].copy()
comb["RSI_Position"] = rsi_df.loc[:, ["RSI_Position"]]
comb["Comb_Position"] = np.where(comb["RSI_Position"] == comb["MACD_Position"], comb["MACD_Position"], 0)
print(comb["Comb_Position"].value_counts())
comb["Comb_Trades"] = comb["Comb_Position"].diff().fillna(0).abs()

# At a row level
comb["Comb_Strategy"] = comb["Returns"] * comb["Comb_Trades"].shift(1)
comb["Comb_Strategy_Net"] = comb["Returns"] - comb["Comb_Trades"] * trading_cost

# Cumulative level
comb["CReturns"] = comb["Returns"].cumsum().apply(np.exp)
comb["CComb_Strategy"] = comb["Comb_Strategy"].cumsum().apply(np.exp)
comb["CComb_Strategy_Net"] = comb["Comb_Strategy_Net"].cumsum().apply(np.exp)

comb[["CComb_Strategy", "CComb_Strategy_Net", "CReturns"]].plot(figsize=(12, 8), title="EURUSD - Combined Strategy")
plt.show()





