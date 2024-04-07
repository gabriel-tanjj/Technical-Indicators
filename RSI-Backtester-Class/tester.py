from backtester import RSIBacktester as rsi

test = rsi("EURUSD=X", 20, 70, 30, "2004-01-01", "2020-01-01", 0.00007)
test.get_data()
test.test_strategy()
test.plot_results()
test.update_for_brute((20, 70, 30))
print(test.optimize((10,50,1), (50,95,1), (5,50,1)))
test.set_parameters(10, 56.7, 47)
test.plot_results()