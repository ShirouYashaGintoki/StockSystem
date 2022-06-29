import pandas as pd
from pandas import json_normalize
import requests
from tabulate import tabulate


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
