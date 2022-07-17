import yfinance as yf
import datetime

tod = datetime.datetime.now()
d = datetime.timedelta(days = 7)
a = tod - d
start = a.strftime("%Y-%m-%d")
end = tod.strftime("%Y-%m-%d")
# start = a.strftime("%d-%m-%Y")
# end = tod.strftime("%d-%m-%Y")
print(f'Today: {tod} -> Yesterday: {a}')

apple= yf.Ticker("aapl")
applehist = apple.history(period='1wk', interval='1d', start=start, end=end, auto_adjust=False, rounding=True)
applehist = applehist.iloc[::-1]
applehist.drop(['Dividends', 'Adj Close', 'Stock Splits'], axis=1, inplace=True)
print(applehist)

day1Close = applehist.Close.iloc[0]
day2Close = applehist.Close.iloc[1]

print(day1Close, day2Close)
percent_diff = (((float(day1Close) - float(day2Close))/float(day2Close)) * 100)
prefix = "+" if percent_diff > 0 else ''
print(f'Difference is {prefix}{percent_diff:.2f}%')

