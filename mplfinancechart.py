import pandas as pd
from pandas import json_normalize
import requests
from tabulate import tabulate
import matplotlib as plt
import time
import threading
import numpy as np
import mplfinance as mf
from datetime import datetime as dtInner

def printSomething():
    print("This should happen in the background")

class RepeatedTimer(object):
     def __init__(self, interval, function, *args, **kwargs):
          self._timer = None
          self.interval = interval
          self.function = function
          self.args = args
          self.kwargs = kwargs
          self.is_running = False
          self.next_call = time.time()
          self.start()

     def _run(self):
          self.is_running = False
          self.start()
          self.function(*self.args, **self.kwargs)

     def start(self):
          if not self.is_running:
               self.next_call += self.interval
               self._timer = threading.Timer(self.next_call - time.time(), self._run)
               self._timer.start()
               self.is_running = True

     def stop(self):
          self._timer.cancel()
          self.is_running = False

def makeFloat(given):
     fixed = float(given)
     return fixed

def makeInt(given):
     fixed = int(given)
     return fixed


# URL for API
url = "https://twelve-data1.p.rapidapi.com/time_series"

# Headers for API
headers = {
    'x-rapidapi-host': "twelve-data1.p.rapidapi.com",
    'x-rapidapi-key': "d9d76c3270msh16a19417bd4b485p1b0395jsn955227be6f56"
}


querystring = {"symbol":"NFLX","interval":"1h","outputsize":"30","format":"json"}
response = requests.request("GET", url, headers=headers, params=querystring)
jsonResponse = response.json()
df2 = json_normalize(jsonResponse, 'values')
df2 = df2.iloc[::-1]
df2.index = pd.DatetimeIndex(df2['datetime'])
df2.drop(['datetime'], axis=1, inplace=True)
df2['open'] = df2['open'].apply(makeFloat)
df2['high'] = df2['high'].apply(makeFloat)
df2['low'] = df2['low'].apply(makeFloat)
df2['close'] = df2['close'].apply(makeFloat)
df2['volume'] = df2['volume'].apply(makeInt)

# _5minThread = RepeatedTimer(5, printSomething)

df2['EMA12'] = df2.close.ewm(span=12).mean()
df2['EMA26'] = df2.close.ewm(span=26).mean()
df2['MACD'] = df2.EMA12 - df2.EMA26
df2['sigval'] = df2.MACD.ewm(span=9).mean()
df2['selector'] = ""


for i in range(1, len(df2)):
     if df2.MACD.iloc[i] > df2.sigval.iloc[i] and df2.MACD.iloc[i-1] < df2.sigval.iloc[i-1]:
          df2.iloc[[i], 9] = 'BUY'
     elif df2.MACD.iloc[i] < df2.sigval.iloc[i] and df2.MACD.iloc[i-1] > df2.sigval.iloc[i-1]:
          df2.iloc[[i], 9] = 'SELL'
     else:
          df2.iloc[[i], 9] = np.nan

buySignals = df2.query('selector == "BUY"')
sellSignals = df2.query('selector == "SELL"')

buyValues = buySignals['close'].tolist()
sellValues = sellSignals['close'].tolist()

print(buyValues)
print(sellValues)

buy_markers = mf.make_addplot(buyValues, type='scatter', markersize=120, marker='^')
sell_markers = mf.make_addplot(sellValues, type='scatter', markersize=120, marker='v')

apds = [buy_markers, sell_markers]
df3 = df2
df3.drop(['EMA12', 'EMA26', 'MACD', 'sigval', 'selector'], axis=1, inplace=True)

print("NORMAL DF")
print(tabulate(df2, showindex=True, headers=list(df2.columns)))
print("------------------------------")

print("CHART DF")
print(tabulate(df3, showindex=True, headers=list(df3.columns)))
print("------------------------------")

# mf.plot(df3, type="candle", addplot=apds)

# mf.plot(df2)

# _5minThread.stop()