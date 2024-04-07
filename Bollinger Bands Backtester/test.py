from backtester import Backtest

data = Backtest(30, 2, 0.00007, 4.93)
data.get_data()
data.test_strategy()
data.plot_data()
data.update_strategy((20, 2))
data.optimize((10, 100, 1), (0.5, 10, 0.5))
data.set_parameters(58, 1)
data.test_strategy()
data.plot_data()
data.financial_analysis()

