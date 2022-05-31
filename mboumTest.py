import requests
import pandas as pd
import tabulate
# from datetime import datetime
import datetime as dtOver
from datetime import datetime as dtInner
from dateutil import tz
# from guppy import hpy; h=hpy()
# import gc

url = "https://mboum-finance.p.rapidapi.com/hi/history"

querystring = {"symbol":"AAPL","interval":"15m","diffandsplits":"false"}

headers = {
	"X-RapidAPI-Host": "mboum-finance.p.rapidapi.com",
	"X-RapidAPI-Key": "d9d76c3270msh16a19417bd4b485p1b0395jsn955227be6f56"
}

df = pd.DataFrame(columns=['date_utc', 'date_gmt', 'date', 'open', 'high', 'low', 'close', 'volume'])

response = requests.request("GET", url, headers=headers, params=querystring)
jsonResponse = response.json()
items = jsonResponse['items']
items = dict(reversed(list(items.items())))
from_zone = tz.gettz('UTC')
to_zone = tz.gettz('Europe/London')
count = 0
#Europe/London
for row in items:
	if count != 10:
		someDf = pd.DataFrame([items[row]])
		utc = dtInner.fromtimestamp(someDf.at[0, 'date_utc'], dtOver.timezone.utc).strftime("%d-%m-%Y %H:%M:%S")
		utc = dtInner.strptime(str(utc), '%d-%m-%Y %H:%M:%S')
		# someDf.at[0, 'date_utc'] = utc
		utc = utc.replace(tzinfo=from_zone)
		central = utc.astimezone(to_zone)
		central = central.strftime('%d-%m-%Y %H:%M:%S')
		someDf.at[0, 'date_gmt'] = central
		# someDf.at[0, 'date_utc'] = dtInner.fromtimestamp(someDf.at[0, 'date_utc'], dtOver.timezone.utc).strftime("%d-%m-%Y %H:%M:%S")
		df = pd.concat([df, someDf], ignore_index=True)		
		count += 1
	else:
		break
df.drop(['date_utc', 'open', 'high', 'low', 'volume'], axis=1, inplace=True)
print(df)
# print("Before deletion\n-----------")
# print(h.heap())
# del response
# del jsonResponse
# gc.collect()
# print("After deletion\n-----------")
# print(h.heap())