import pymysql
import sqlalchemy
import pandas as pd
import numpy as np
from tkinter import messagebox
import mplfinance as mpf
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read("config.ini")
dbInfo = config_object["DATABASE"]

timeFrameDict = {
     "5MIN" : "5min",
     "30MIN" : "30min",
     "1HOUR" : "1h"
}

# Indices as dataframe, Sheet 1 is main sheet, Sheet 2 has 5 for testing
indices = pd.read_excel('tickers2.xlsx', sheet_name='Sheet 1')
# Create a dictionary of stock names and their ticker symbols
indDict = pd.Series(indices.Symbol.values, index=indices.CompanyName).to_dict()

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
               else:
                    print("List 2 true, list 1 false")
                    sellPoints = [np.NaN if j is None else j for j in sellPoints]
                    apds = [
                         mpf.make_addplot(sellPoints, type="scatter", markersize=120, marker="^"),
                         mpf.make_addplot(macd, panel=1, color="fuchsia", secondary_y=False),
                         mpf.make_addplot(sigval, panel=1, color="b", secondary_y=False),
                    ]
                    print(f"{sellPoints} / {len(sellPoints)}")
          mpf.plot(results,type='candle',addplot=apds,figscale=1.1,figratio=(8,5),title='\n'+ticker+' '+ timeframe, style='blueskies',panel_ratios=(6,3))
     except Exception as e:
          messagebox.showerror("ERROR", """There is currently no data for this stock timeframe pairing.\nPlease wait until the next interval before trying again.""")
          print(e)