from Backtester import Backtester

tester = Backtester("EURUSD=X", short_len=50, long_len=200,
                    start_date="2010-01-01", end_date="2015-01-01", trading_cost=0.00007)

print(tester.get_data())

# tester.test_strategy()
# tester.plot_data()
# tester.update_strategy((50,300))

tester.test_strategy()

print(tester.update_strategy_brute(SMA=(50, 200)))

print(tester.optimize((10, 50, 1), (100, 250, 1)))

tester.update_strategy_no_optimize(SMA=(47,140))


