from ema_backtest import Backtester

data = Backtester(ticker="EURUSD=X", short_len=10,
                  long_len=20, start_date="2015-01-01", end_date="2020-01-01", trading_cost=0.00007)

data.get_data()
data.test_strategy()

print(data.update_strategy_brute(EMA=(50,200)))
print(data.optimize((10,100,1), (200,300,1)))
data.set_parameters(15, 289)
data.plot_data()



