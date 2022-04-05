import matplotlib.pyplot as plt
import requests
import sqlite3 as db
import time
import pandas as pd
from pandas import json_normalize

dataFrames = []

url = "https://twelve-data1.p.rapidapi.com/time_series"

# querystring = {"symbol":"ALV.DE","interval":"1h","outputsize":"1","format":"json"}

headers = {
    'x-rapidapi-host': "twelve-data1.p.rapidapi.com",
    'x-rapidapi-key': "d9d76c3270msh16a19417bd4b485p1b0395jsn955227be6f56"
    }

indices = pd.read_excel('tickers2.xlsx', sheet_name='Sheet 2')

tickers = indices['Symbol']

linecount = 0

for ticker in tickers:
    print(ticker, end=" ")
    linecount += 1
    if linecount % 5 == 0:
        time.sleep(60)
    try:
        querystring = {"symbol":ticker,"interval":"1h","outputsize":"1","format":"json"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        jsonResponse = response.json()
        df2 = json_normalize(jsonResponse, 'values')
        print(df2)
        # print(jsonResponse)
    except Exception as e:
        print(ticker + " " + str(e))
