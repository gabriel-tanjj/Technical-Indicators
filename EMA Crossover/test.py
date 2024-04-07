from backtester_class import Backtester

data = Backtester("EURUSD=X", 100, 50, "2019-01-01", "2020-01-01", 0.00007)

print(data.get_data())
print(data.test_strategy())
print(data.update_strategy_brute(param=(100, 50)))
print(data.optimize((50,200,1), (10,100,1)))
data.set_parameters(63, 74)
data.test_strategy()
data.plot_data()
