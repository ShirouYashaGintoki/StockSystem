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

df = pd.read_excel('tickers2.xlsx', sheet_name='Sheet 1')

tickers = df['Symbol']