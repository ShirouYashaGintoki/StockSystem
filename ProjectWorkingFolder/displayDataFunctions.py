import pymysql
import sqlalchemy
import pandas as pd
import numpy as np
from tkinter import messagebox
import mplfinance as mpf
from configparser import ConfigParser
from tabulate import tabulate
import datetime as dtOuter
from datetime import datetime as dtInner
from dateutil import tz
import yfinance as yf

config_object = ConfigParser()
config_object.read("config.ini")
dbInfo = config_object["DATABASE"]

timeFrameDict = {
     "5MIN" : "5min",
     "30MIN" : "30min",
     "1HOUR" : "1h"
}

# Indices as dataframe, Sheet 1 is main sheet, Sheet 2 has 5 for testing
indices = pd.read_excel('tickers.xlsx', sheet_name='Sheet 1')
# Create a dictionary of stock names and their ticker symbols
indDict = pd.Series(indices.Symbol.values, index=indices.CompanyName).to_dict()
# Create a list of stock names for display purposes
tickerSymbolList = sorted(list(indDict.values()))

# Set time zones as data received is in US timezone
from_zone = tz.gettz('America/New_York')
apiFormat = "%Y-%m-%d %H:%M:%S"
ukFormat = "%d-%m-%Y %H:%M:%S"
local_zone = tz.tzlocal()

# Dataframe to hold the records of the current signals to prevent duplicate signals
currentSignals = pd.DataFrame(columns=["datetime", "assetname", "open", "high", "low", "close", "volume", "ema12", "ema26", "macd", "sigval", "selector"])

def findNameFromTicker(name):
    findKey = ""
    for key, value in indDict.items():
        if name == value:
            findKey = key
    return findKey

# df['col1'] = df['col1'].apply(complex_function)
# Function to convert given datetime from US/New York timezone
# into local timezone (GMT/BST)
# Args
# datetime -> A value from the column that is given
def convertTimezone(timeInColumn):
     dt_utc = str(timeInColumn)
     dt_utc = dtInner.strptime(dt_utc, apiFormat)
     dt_utc = dt_utc.replace(tzinfo=from_zone)
     dt_local = dt_utc.astimezone(local_zone)
     local_time_str = dt_local.strftime(ukFormat)
     return local_time_str

def makeFloat(given):
     fixed = float(given)
     return fixed

def makeInt(given):
     fixed = int(given)
     return fixed

def retrieveDataOneTf(listOfAssets, timeframe):
     pymysql.install_as_MySQLdb()
     engine = sqlalchemy.create_engine(dbInfo["dblink"])
     listOfFrames = []
     for asset in listOfAssets:
          query = f'''
          SELECT *
          FROM {asset+timeframe}
          ORDER BY datetime DESC LIMIT 30;'''
          df = pd.read_sql(query, engine)
          listOfFrames.append(df)
     return pd.concat(listOfFrames)

# Function to display chart with signal indicators
# ticker -> Given ticker
# timeframe -> Given timeframe
def displayChartWithSignals(ticker, timeframe):
     try:
          accessTf = timeFrameDict[timeframe]
          # Retrieve last 30 (or 60) results from the database
          results = retrieveDataOneTf([indDict[ticker]], accessTf)
          results.index = pd.DatetimeIndex(results['datetime'])
          results.drop(['datetime'], axis=1, inplace=True)
          results['open'] = results['open'].apply(makeFloat)
          results['high'] = results['high'].apply(makeFloat)
          results['low'] = results['low'].apply(makeFloat)
          results['close'] = results['close'].apply(makeFloat)
          results['volume'] = results['volume'].apply(makeInt)
          results['volume'].apply(lambda x: '%.12f' % x)
          print("Results for chart")
          results = results.iloc[::-1]
          print(results)

          buyPoints = []
          sellPoints = []

          counter = 0
          for i in range(0, len(results)):
               if counter == 0:
                    counter += 1
                    buyPoints.append(np.nan)
                    sellPoints.append(np.nan)
                    continue
               else:
                    if results.selector.iloc[i] == "BUY":
                         buyPoints.append(results.close.iloc[i] * 0.995)
                    else:
                         buyPoints.append(np.nan)
                    
                    if results.selector.iloc[i] == "SELL":
                         sellPoints.append(results.close.iloc[i] * 1.005)
                    else:
                         sellPoints.append(np.nan)

          # print(buyPoints)
          # print(sellPoints)
          # macd = results.ema12 - results.ema26
          macd = results['macd'].tolist()
          # sigval = results.macd.ewm(span=9).mean()
          sigval = results['sigval'].tolist()
          buyPoints = [None if i is np.nan else i for i in buyPoints]
          sellPoints = [None if i is np.nan else i for i in sellPoints]
          if any(isinstance(j, float) for j in buyPoints) and any(isinstance(i, float) for i in sellPoints):
               print("Both true")
               buyPoints = [np.nan if i is None else i for i in buyPoints]
               sellPoints = [np.nan if j is None else j for j in sellPoints]
               apds = [
                    mpf.make_addplot(buyPoints, type="scatter", markersize=120, marker="^"),
                    mpf.make_addplot(sellPoints, type="scatter", markersize=120, marker="v"),
                    mpf.make_addplot(macd, panel=1, color="fuchsia", secondary_y=False),
                    mpf.make_addplot(sigval, panel=1, color="b", secondary_y=False),
               ]
               print(f"{buyPoints} / {len(buyPoints)}")
               print(f"{sellPoints} / {len(sellPoints)}")
          else:
               if any(isinstance(j, float) for j in buyPoints) and not any(isinstance(i, float) for i in sellPoints):
                    print("List 1 true, list 2 false")
                    buyPoints = [np.nan if i is None else i for i in buyPoints]
                    apds = [
                         mpf.make_addplot(buyPoints, type="scatter", markersize=120, marker="^"),
                         mpf.make_addplot(macd, panel=1, color="fuchsia", secondary_y=False),
                         mpf.make_addplot(sigval, panel=1, color="b", secondary_y=False),
                    ]
                    print(f"{buyPoints} / {len(buyPoints)}")
               elif any(isinstance(j, float) for j in sellPoints) and not any(isinstance(i, float) for i in buyPoints):
                    print("List 2 true, list 1 false")
                    sellPoints = [np.NaN if j is None else j for j in sellPoints]
                    apds = [
                         mpf.make_addplot(sellPoints, type="scatter", markersize=120, marker="^"),
                         mpf.make_addplot(macd, panel=1, color="fuchsia", secondary_y=False),
                         mpf.make_addplot(sigval, panel=1, color="b", secondary_y=False),
                    ]
                    print(f"{sellPoints} / {len(sellPoints)}")
               else:
                    print("No signals, displaying normal chart")
                    apds = [
                         mpf.make_addplot(macd, panel=1, color="fuchsia", secondary_y=False),
                         mpf.make_addplot(sigval, panel=1, color="b", secondary_y=False),
                    ]
          mpf.plot(results,type='candle',addplot=apds,figscale=1.1,figratio=(8,5),title='\n'+ticker+' '+ timeframe, style='blueskies',panel_ratios=(6,3))
     except Exception as e:
          messagebox.showerror("ERROR", """There is currently no data for this stock timeframe pairing.\nPlease wait until the next interval before trying again.""")
          print(e)

# Display new signals to board
def displayChart(dfOfSignals, displayBox):
     try:
          # Query dataframe argument to select only signal records
          results = dfOfSignals.query('selector == "BUY" or selector == "SELL"')
          # Drop the rowid to compare with currentSignals
          # results = results.drop(['rowid'], axis=1, errors='ignore')
          results.sort_values(by=['datetime'])
          # Print results for checking
          print("Initial results")
          print(tabulate(results, showindex=False, headers=results.columns))
          # results = results.drop_duplicates(keep='first')
          # Make currentSignals global to allow it to be accessed as local in the function
          global currentSignals
          # Print 
          print("Current Signals dataframe")
          print(tabulate(currentSignals, showindex=False, headers=results.columns))
          results = results[~results.apply(tuple,1).isin(currentSignals.apply(tuple,1))]
          # if results[9] != "BUY" or results[9] != "SELL":
          #      results.shift(1, axis=1)
          print("Results after filter attempt")
          print(tabulate(results, showindex=False, headers=results.columns))
          currentSignals = pd.concat([results, currentSignals], ignore_index=True)
          print("Current signals after adding results")
          print(tabulate(currentSignals, showindex=False, headers=results.columns))
          # Trying to convert date format into local as string because MySQL only accepts
          # YYYY-MM-DD format, not the UK format
          print("Current signals after converting date format")
          results['datetime'] = results['datetime'].apply(convertTimezone)
          print(tabulate(results, showindex=True, headers=list(results.columns)))
          results = results.sort_values(by=['datetime'])
          if not results.empty:
               print("Results sorted by datetime")
               print(tabulate(results, showindex=False, headers=results.columns))
               for row in results.itertuples():
                    if row[13] == "BUY":
                         displayBox.configure(state="normal")
                         assetName = row[3]
                         signalDt = row[2]
                         closePrice = row[7]
                         assetInputString = f'BUY: {assetName}\n'
                         displayBox.insert('end', assetInputString, 'BUY')
                         inputString = f"""Date/Time: {str(signalDt)}\nClose Price: {closePrice:.2f}\n---------------------------------------------\n"""
                         displayBox.insert('end', inputString)
                         print(inputString)
                    elif row[13] == "SELL":
                         displayBox.configure(state="normal")
                         assetName = row[3]
                         signalDt = row[2]
                         closePrice = row[7]
                         assetInputString = f'SELL: {assetName}\n'
                         displayBox.insert('end', assetInputString, 'SELL')
                         inputString = f"""Date/Time: {str(signalDt)}\nClose Price: {closePrice:.2f}\n---------------------------------------------\n"""
                         displayBox.insert('end', inputString)
                         print(inputString)
               displayBox.configure(state="disabled")
          else:
               print("Nothing available")
               displayBox.configure(state="normal")
               displayBox.insert('end', "Nothing to add")
               displayBox.configure(state="disabled")
     except Exception as e:
          print("DisplayBox error " + str(e))

def getRecentDayPctDiff(top5Box, bot5Box):
     tod = dtInner.now()
     d = dtOuter.timedelta(days = 7)
     a = tod - d
     start = a.strftime("%Y-%m-%d")
     end = tod.strftime("%Y-%m-%d")
     listOfFrames = []
     # print(f'Today: {tod} -> Yesterday: {a}')
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
     prefix = ""
     top5Box.configure(state="normal")
     bot5Box.configure(state="normal")
     top5Box.delete('1.0', "end")
     bot5Box.delete('1.0', "end")
     for row in top5.itertuples():
          prefix = "+" if row[2] > 0 else ""
          insertText = f'Asset: {findNameFromTicker(row[1])} | Pct Change: {prefix}{row[2]:.2f}%\n'
          top5Box.insert("end", insertText)
          print(f'Asset: {findNameFromTicker(row[1])} | Pct Change: {prefix}{row[2]:.2f}%')
     for row in bot5.itertuples():
          prefix = "+" if row[2] > 0 else ""
          insertText = f'Asset: {findNameFromTicker(row[1])} | Pct Change: {prefix}{row[2]:.2f}%\n'
          bot5Box.insert("end", insertText)
          print(f'Asset: {findNameFromTicker(row[1])} | Pct Change: {prefix}{row[2]:.2f}%')
     top5Box.configure(state="disabled")
     bot5Box.configure(state="disabled")