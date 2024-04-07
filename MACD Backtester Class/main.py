from ema_backtester import Backtester

test = Backtester("EURUSD", 12, 26, 9, "2015-01-01", "2020-01-01", 0.00007)
test.get_data()
test.test_strategy()
test.plot_results()
test.optimize((10,30,1), (20,60,1), (1, 20, 1))
test.set_parameters(29, 28, 2)
test.plot_results()