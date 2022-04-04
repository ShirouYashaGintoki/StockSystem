import requests
import sqlite3 as db
import time
import json
import pandas as pd

indices = []

url = "https://twelve-data1.p.rapidapi.com/time_series"

# querystring = {"symbol":"ALV.DE","interval":"1h","outputsize":"1","format":"json"}

headers = {
    'x-rapidapi-host': "twelve-data1.p.rapidapi.com",
    'x-rapidapi-key': "d9d76c3270msh16a19417bd4b485p1b0395jsn955227be6f56"
    }

df = pd.read_excel('tickers2.xlsx', sheet_name='Sheet 1')

tickers = df['Symbol']

linecount = 0

passes = []
fails = []


# response = requests.request("GET", url, headers=headers, params=querystring)
# jsonResponse = response.json()

for ticker in tickers:
    linecount += 1
    if linecount % 5 == 0:
        time.sleep(60)
    try:
        querystring = {"symbol":ticker,"interval":"1h","outputsize":"1","format":"json"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        jsonResponse = response.json()
        if jsonResponse["status"] == "error":
            fails.append(jsonResponse["meta"]["symbol"])
        else:
            passes.append(jsonResponse["meta"]["symbol"])
        # print(jsonResponse)
    except Exception as e:
        print(ticker + " " + str(e))

print("###############\n")

print("Passes: ", end="")
for good in passes:
    print(good, end=", ")

print("\nFails: ", end="")
for fail in fails:
    print(fail, end=", ")
# Errors


# for ticker in tickers:
#     print(ticker)

# response = requests.request("GET", url, headers=headers, params=querystring)
# jsonResponse = response.json()

# print('JSON Response')
# for item in jsonResponse['values']:
#     print(item, end='\n')

# with open('tickers.txt') as f:
#     linecount = 0
#     for line in f:
#         linecount += 1
#         if linecount % 5 == 0:
#             time.sleep(60)
#         try:
#             index = line
#             querystring = {"symbol":index,"interval":"1h","outputsize":"1","format":"json"}
#             response = requests.request("GET", url, headers=headers, params=querystring)
#             jsonResponse = response.json()
#             print(jsonResponse)
#         except:
#             print("There was an error")

