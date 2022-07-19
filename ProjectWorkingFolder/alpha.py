import requests
import pandas as pd
import json

url = "https://alpha-vantage.p.rapidapi.com/query"

querystring = {"interval":"5min","function":"TIME_SERIES_INTRADAY","symbol":"MSFT","datatype":"json","output_size":"compact"}

headers = {
	"X-RapidAPI-Key": "d9d76c3270msh16a19417bd4b485p1b0395jsn955227be6f56",
	"X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"
}

response = requests.request("GET", url, headers=headers, params=querystring)
jsonResponse = response.json()
df2 = pd.json_normalize(jsonResponse, record_path="Time Series (5min)"g)
# df2 = pd.json_normalize(jsonResponse["Time Series (5min)"])
# print(df2.head(5))