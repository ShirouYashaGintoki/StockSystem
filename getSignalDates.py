import matplotlib.pyplot as plt
import requests
import sqlite3 as db
import time
import pandas as pd
from pandas import json_normalize
from tabulate import tabulate

# List of dataframes for each stock
dataFrames = []

# URL for API
url = "https://twelve-data1.p.rapidapi.com/time_series"

# querystring = {"symbol":"ALV.DE","interval":"1h","outputsize":"1","format":"json"}

# Headers for API
headers = {
    'x-rapidapi-host': "twelve-data1.p.rapidapi.com",
    'x-rapidapi-key': "d9d76c3270msh16a19417bd4b485p1b0395jsn955227be6f56"
    }

# Indices as dataframe, Sheet 1 is main sheet, Sheet 2 has 5 for testing
indices = pd.read_excel('tickers2.xlsx', sheet_name='Sheet 2')

# Tickers is a list of symbols as strings from the 'Symbol' column
# of the dataframe 'indices'
tickers = indices['Symbol']

# Begin a linecount to initiate a waiting period when API limits are reached
linecount = 0

# Iterate through tickers
for ticker in tickers:
    # Print tickers
    print(ticker)
    # Increment linecount
    linecount += 1
    # If linecount is a multiple of 5 (5 requests per minute)
    if linecount % 5 == 0:
        # Sleep for a minute
        time.sleep(60)
    try:
        querystring = {"symbol":ticker,"interval":"1h","outputsize":"30","format":"json"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        jsonResponse = response.json()
        df2 = json_normalize(jsonResponse, 'values')
        df2['EMA12'] = df2.close.ewm(span=12).mean()
        df2['EMA26'] = df2.close.ewm(span=26).mean()
        df2['MACD'] = df2.EMA12 - df2.EMA26
        df2['signal'] = df2.MACD.ewm(span=9).mean()
        df2.drop('volume', axis=1, inplace=True)
        print(tabulate(df2, showindex=False, headers=list(df2.columns)))
        # print(df2.to_markdown())
        # df2.head()
        # print(df2)
        # print(jsonResponse)
    except Exception as e:
        print(ticker + " " + str(e))
