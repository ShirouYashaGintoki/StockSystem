import pandas as pd
from pandas import json_normalize
import requests
from tabulate import tabulate
import matplotlib as plt
import time
import threading
import numpy as np
import mplfinance as mpf
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


querystring = {"symbol":"TSLA","interval":"5min","outputsize":"30","format":"json"}
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
df2['volume'].apply(lambda x: '%.12f' % x)

# _5minThread = RepeatedTimer(5, printSomething)

df2['EMA12'] = df2.close.ewm(span=12).mean()
ema12 = df2.close.ewm(span=12).mean()
df2['EMA26'] = df2.close.ewm(span=26).mean()
ema26 = df2.close.ewm(span=26).mean()
df2['MACD'] = df2.EMA12 - df2.EMA26
macd = df2.EMA12 - df2.EMA26
df2['sigval'] = df2.MACD.ewm(span=9).mean()
sigval = df2.MACD.ewm(span=9).mean()
df2['selector'] = ""

buyPoints = []
sellPoints = []

counter = 0
for i in range(0, len(df2)):
     if counter == 0:
          counter += 1
          buyPoints.append(np.nan)
          sellPoints.append(np.nan)
          continue
     if df2.MACD.iloc[i] > df2.sigval.iloc[i] and df2.MACD.iloc[i-1] < df2.sigval.iloc[i-1]:
          df2.iloc[[i], 9] = 'BUY'
          buyPoints.append(df2.close.iloc[i] * 0.98)
     else:
          buyPoints.append(np.nan)

     if df2.MACD.iloc[i] < df2.sigval.iloc[i] and df2.MACD.iloc[i-1] > df2.sigval.iloc[i-1]:
          df2.iloc[[i], 9] = 'SELL'
          sellPoints.append(df2.close.iloc[i] * 1.02)
     else:
          sellPoints.append(np.nan)


buySignals = df2.query('selector == "BUY"')
sellSignals = df2.query('selector == "SELL"')

buyValues = buySignals['close'].tolist()
sellValues = sellSignals['close'].tolist()

# buy_markers = mpf.make_addplot(buyPoints, type='scatter', markersize=120, marker='^')
# sell_markers = mpf.make_addplot(sellPoints, type='scatter', markersize=120, marker='v')

# apds = [buy_markers, sell_markers]
df3 = df2
df3.drop(['EMA12', 'EMA26', 'MACD', 'sigval', 'selector'], axis=1, inplace=True)

print("NORMAL DF")
print(df2)
print("------------------------------")

print("CHART DF")
print(df3)
print("------------------------------")

print('size of x = {0}'.format(df2.index.size))
print('size of y = {0}'.format(df2['close'].size))

print(f'{buyPoints} / {len(buyPoints)}')
print(f'{sellPoints} / {len(sellPoints)}')

# MACD WORKS -> REMEMBER THIS

apds = [
          mpf.make_addplot(buyPoints, type='scatter', markersize=120, marker='^'),
          mpf.make_addplot(sellPoints, type='scatter', markersize=120, marker='v'),
          mpf.make_addplot(macd,panel=1,color='fuchsia',secondary_y=True),
          mpf.make_addplot(sigval,panel=1,color='b',secondary_y=True)
]

mpf.plot(df2,type='candle',addplot=apds,figscale=1.1,figratio=(8,5),title='\nMACD',
         style='blueskies',panel_ratios=(6,3))



# mf.plot(df2)

# _5minThread.stop()