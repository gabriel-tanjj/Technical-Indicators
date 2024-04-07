from so_backtester import Backtester

test = Backtester(14, 3, "2010-01-01", "2020-01-01", 0.00007)

test.get_data()
test.test_strategy()
test.plot_results()
test.update((14,3))
test.optimize((10, 100, 1), (1, 100, 1))
test.set_parameters(13, 12)
test.plot_results()