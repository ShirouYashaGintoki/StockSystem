import pandas as pd
from pandas import json_normalize
import requests
from tabulate import tabulate
import plotly.express as px
import plotly.graph_objects as go
import time
import threading

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

# URL for API
url = "https://twelve-data1.p.rapidapi.com/time_series"

# Headers for API
headers = {
    'x-rapidapi-host': "twelve-data1.p.rapidapi.com",
    'x-rapidapi-key': "d9d76c3270msh16a19417bd4b485p1b0395jsn955227be6f56"
}

querystring = {"symbol":"AAPL","interval":"5m","outputsize":"30","format":"json"}
response = requests.request("GET", url, headers=headers, params=querystring)
jsonResponse = response.json()
df2 = json_normalize(jsonResponse, 'values')
df2.drop(['open', 'high', 'low', 'volume'], axis=1, inplace=True)
df2 = df2.iloc[::-1]
