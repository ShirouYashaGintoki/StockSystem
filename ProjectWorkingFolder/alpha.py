import requests
import pandas as pd
import json

url = "https://alpha-vantage.p.rapidapi.com/query"

querystring = {"interval":"5min","function":"TIME_SERIES_INTRADAY","symbol":"MSFT","datatype":"json","output_size":"compact"}

headers = {
	"X-RapidAPI-Key": "d9d76c3270msh16a19417bd4b485p1b0395jsn955227be6f56",
	"X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"
}

df = pd.DataFrame(columns=["datetime", "open", "high", "low", "close", "volume"])

response = requests.request("GET", url, headers=headers, params=querystring)
jsonResponse = response.json()
items = jsonResponse["Time Series (5min)"]
count = 0
for row in items:
	if count != 30:
		someDf = pd.DataFrame([items[row]])
		someDf["datetime"] = row
		someDf.rename(columns={"1. open": "open", "2. high": "high", "3. low": "low", "4. close": "close", "5. volume": "volume"}, inplace=True)
		df = pd.concat([df, someDf], ignore_index=True)

print(df.head(5))
# print(items)
# df2 = pd.json_normalize(jsonResponse["Time Series (5min)"])
# print(df2.head(5))