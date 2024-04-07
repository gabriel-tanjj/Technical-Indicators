import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-v0_8')

SHORT_LEN = 20
LONG_LEN = 50
# Spread for open & close position is 1.5
SPREAD_COST = 1.5 * 0.0001
COMMISSION = 0
SPREAD_PER_TRADE = SPREAD_COST/2


data = pd.read_csv('eurusd.csv', parse_dates=['Date'], index_col='Date')

# Add new column for SMA short & SMA Long
data['SMA-S'] = data.price.rolling(SHORT_LEN).mean()
data['SMA-L'] = data.price.rolling(LONG_LEN).mean()

# data.plot(figsize=(12,8), title="EUR/USD-SMA SMA{} | SMA{}".format(SHORT_LEN, LONG_LEN), fontsize=12)
plt.legend(fontsize=12)

data['Position'] = np.where(data['SMA-S'] > data['SMA-L'], 1, -1)

data.loc['2019':, ['SMA-S', 'SMA-L', 'Position']].plot(figsize=(12,8), fontsize=12, secondary_y='Position', title="EUR/USD-SMA SMA{} | SMA{}".format(SHORT_LEN, LONG_LEN))

data['Returns'] = np.log(data.price.div(data.price.shift(1)))
data["Strategy"] = data.Position.shift(1) * data["Returns"]

# If the diff in position is 0, trade is being held
# However, if the diff is 2 (from -1 to 1 or 1 to -1), there is a change in position
data["Trades"] = data.Position.diff().fillna(0).abs()

print(data[["Returns", "Strategy"]].sum())
# Annualized risk is daily std for both returns / strategy * sqrt of time
print(data[["Returns", "Strategy"]].std() * np.sqrt(252))
# Annualized returns
print(data[["Returns", "Strategy"]].mean() * 252)
# Cumsum of returns
# Due to the multiplicative nature of returns we cannot have an additive cumsum of "returns"
# Thus we have to exponentiate it by using np.exp
data["CReturns"] = data["Returns"].cumsum().apply(np.exp)
# Cumsum of strategy returns
data["CStrategy"] = data["Strategy"].cumsum().apply(np.exp)
data["Net_Strategy"] = data.Strategy - data.Trades * SPREAD_PER_TRADE
data["CNet_Strategy"] = data.Net_Strategy.cumsum().apply(np.exp)

data["Outperformance"] = data.CStrategy - data.CReturns

data[["CReturns", "CStrategy", "Outperformance", "CNet_Strategy"]].plot(figsize=(12, 8), title="EUR/USD - SMA{} | SMA{}".format(SHORT_LEN, LONG_LEN))


plt.show()

