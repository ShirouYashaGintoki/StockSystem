import yfinance as yf
import datetime
import pandas as pd

# Indices as dataframe, Sheet 1 is main sheet, Sheet 2 has 5 for testing
indices = pd.read_excel('tickers2.xlsx', sheet_name='Sheet 1')
# print(indices)
# Create a dictionary of stock names and their ticker symbols
indDict = pd.Series(indices.Symbol.values, index=indices.CompanyName).to_dict()
# Create a list of stock names for display purposes
tickerSymbolList = sorted(list(indDict.values()))
# print(tickerSymbolList)

def findNameFromTicker(name):
    findKey = ""
    for key, value in indDict.items():
        if name == value:
            findKey = key
    return findKey

def getRecentDayPctDiff():
    tod = datetime.datetime.now()
    d = datetime.timedelta(days = 7)
    a = tod - d
    start = a.strftime("%Y-%m-%d")
    end = tod.strftime("%Y-%m-%d")
    listOfFrames = []
    print(f'Today: {tod} -> Yesterday: {a}')
    for tickerSymbol in tickerSymbolList:
        df = pd.DataFrame(columns=["Symbol", "Percentage Change (%)"])
        if tickerSymbol == "BRK.A": tickerSymbol = "BRK-A"
        tick = yf.Ticker(tickerSymbol)
        tickerHistory = tick.history(period='5d', interval='1d', start=start, end=end, auto_adjust=False, rounding=True)
        tickerHistory = tickerHistory.iloc[::-1]
        tickerHistory.drop(['Dividends', 'Adj Close', 'Stock Splits'], axis=1, inplace=True, errors="ignore")
        tickerHistory = tickerHistory.head(2)

        day1Close = tickerHistory.Close.iloc[0]
        day2Close = tickerHistory.Close.iloc[1]

        # print(day1Close, day2Close)
        percent_diff = (((float(day1Close) - float(day2Close))/float(day2Close)) * 100)
        df.loc[-1] = [tickerSymbol, percent_diff]
        df["Percentage Change (%)"].apply(lambda x: '%.2f' % x)
        listOfFrames.append(df)
    result = pd.concat(listOfFrames)
    result = result.sort_values(by=["Percentage Change (%)"], ascending=False)
    top5 = result.head(5)
    bot5 = result.tail(5)
    bot5 = bot5.iloc[::-1]
    return top5, bot5

        # prefix = "+" if percent_diff > 0 else ''
        # return f'{prefix}{percent_diff:.2f}%'

top5, bot5 = getRecentDayPctDiff()
print("TOP 5")
prefix = ""
for row in top5.itertuples():
    prefix = "+" if row[2] > 0 else ""
    print(f'Asset: {findNameFromTicker(row[1])} | Pct Change: {prefix}{row[2]:.2f}%')
print("\nBOTTOM 5")
for row in bot5.itertuples():
    prefix = "+" if row[2] > 0 else ""
    print(f'Asset: {findNameFromTicker(row[1])} | Pct Change: {prefix}{row[2]:.2f}%')


# tod = datetime.datetime.now()
# d = datetime.timedelta(days = 7)
# a = tod - d
# start = a.strftime("%Y-%m-%d")
# end = tod.strftime("%Y-%m-%d")
# # start = a.strftime("%d-%m-%Y")
# # end = tod.strftime("%d-%m-%Y")
# print(f'Today: {tod} -> Yesterday: {a}')

# apple= yf.Ticker("aapl")
# applehist = apple.history(period='1wk', interval='1d', start=start, end=end, auto_adjust=False, rounding=True)
# applehist = applehist.iloc[::-1]
# applehist.drop(['Dividends', 'Adj Close', 'Stock Splits'], axis=1, inplace=True)
# print(applehist)

# day1Close = applehist.Close.iloc[0]
# day2Close = applehist.Close.iloc[1]

# print(day1Close, day2Close)
# percent_diff = (((float(day1Close) - float(day2Close))/float(day2Close)) * 100)
# prefix = "+" if percent_diff > 0 else ''
# print(f'Difference is {prefix}{percent_diff:.2f}%')

