from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext as st
import pandas as pd
from pandas import json_normalize
import threading
import time
import numpy as np
from datetime import datetime as dtInner
from dateutil import tz
import requests
from tabulate import tabulate
import mysql.connector
import sqlalchemy
import pymysql
import traceback
import mplfinance as mpf
from configparser import ConfigParser
from setupConfigFile import ftConfigSetup


# URL for API
url = "https://twelve-data1.p.rapidapi.com/time_series"

# Headers for API
headers = {
    'x-rapidapi-host': "twelve-data1.p.rapidapi.com",
    'x-rapidapi-key': "d9d76c3270msh16a19417bd4b485p1b0395jsn955227be6f56"
}

# Indices as dataframe, Sheet 1 is main sheet, Sheet 2 has 5 for testing
indices = pd.read_excel('tickers2.xlsx', sheet_name='Sheet 1')
# Create a dictionary of stock names and their ticker symbols
indDict = pd.Series(indices.Symbol.values, index=indices.CompanyName).to_dict()
# Create a list of stock names for display purposes
stockNameList = sorted(list(indDict.keys()))
# print(f'{stockNameList}')

# List of timeframes, to be changed to 5min, 30min, 1h
# 1h has a time signal of HH:30
# 30min is anything either HH:00 or HH:30
# 5min has anything that is a multiple of 5
timeFrames = ['5MIN', '30MIN', '1HOUR']

timeFrameDict = {
     "5MIN" : "5min",
     "30MIN" : "30min",
     "1HOUR" : "1h"
}

# Dictionary to handle rotation of stock, time
# and the current stock/time combination
# Indexes 0 for last, 1 for new stock rotation
# Indexes 2 for last, 3 for new time rotation
# Indexes 4, 5 to store the stock time combination
srtCombo = {
     "clicked1" : ['', '', '', '', '', ''],
     "clicked2" : ['', '', '', '', '', ''],
     "clicked3" : ['', '', '', '', '', ''],
     "clicked4" : ['', '', '', '', '', ''],
     "clicked5" : ['', '', '', '', '', '']
}

# Set time zones as data received is in US timezone
from_zone = tz.gettz('America/New_York')
apiFormat = "%Y-%m-%d %H:%M:%S"
ukFormat = "%d-%m-%Y %H:%M:%S"
local_zone = tz.tzlocal()

# beansontoastA1? for PC
# Establish connection using mysql connector
config_object = ConfigParser()
config_object.read("config.ini")
dbInfo = config_object['DATABASE']
db = mysql.connector.connect(
    host=dbInfo['host'],
    user=dbInfo['user'],
    passwd=dbInfo['password']
)


# Create cursor
my_cursor = db.cursor()

# Try to create database, catch exception if fails
try:
     my_cursor.execute("CREATE DATABASE StockTables")
except Exception:
     print("DB schema already exists")

# Close database connection now
db.close()

# Dataframe to hold the records of the current signals to prevent duplicate signals
currentSignals = pd.DataFrame(columns=["datetime", "assetname", "open", "high", "low", "close", "volume", "ema12", "ema26", "macd", "sigval", "selector"])


# Function to create a table in the database
# for a given asset and timeframe combination
# Args
# assetName -> Given name of asset as string
# timeFrame -> Given time frame as string
def createTable(assetName, timeFrame):
     # Try to establish connection to db schema
     try:
          db = mysql.connector.connect(
               host="localhost",
               user="root",
               passwd="beansontoastA1?",
               database="StockTables"
          )
          # Create cursor
          my_cursor = db.cursor()

          print(timeFrame)
          # Execute query to create table if it doesn't already exist
          my_cursor.execute("""CREATE TABLE IF NOT EXISTS %s (
          rowid INT AUTO_INCREMENT PRIMARY KEY,
          datetime DATETIME,
          assetname varchar(50),
          open FLOAT(5),
          high FLOAT(5),
          low FLOAT(5),
          close FLOAT(5),
          volume INT(7),
          ema12 FLOAT(2),
          ema26 FLOAT(2),
          macd FLOAT(7),
          sigval FLOAT(6),
          selector varchar(4))
          """ %(assetName + timeFrame))
     # Catch any exception and print for debugging
     except Exception as e:
          print(f'Error: {e}')
     # Finally close the cursor to end the function
     finally:
          my_cursor.close()

def makeFloat(given):
     fixed = float(given)
     return fixed

def makeInt(given):
     fixed = int(given)
     return fixed

def retrieveDataOneTf(listOfAssets, timeframe):
     pymysql.install_as_MySQLdb()
     engine = sqlalchemy.create_engine('mysql://root:beansontoastA1?@localhost:3306/stocktables')
     listOfFrames = []
     for asset in listOfAssets:
          query = f'''
          SELECT *
          FROM {asset+timeframe}
          ORDER BY datetime DESC LIMIT 30;'''
          df = pd.read_sql(query, engine)
          listOfFrames.append(df)
     return pd.concat(listOfFrames)
 

# Function to display chart with signal indicators
# ticker -> Given ticker
# timeframe -> Given timeframe
def displayChartWithSignals(ticker, timeframe):
     try:
          accessTf = timeFrameDict[timeframe]
          # Retrieve last 30 (or 60) results from the database
          results = retrieveDataOneTf([indDict[ticker]], accessTf)
          results.index = pd.DatetimeIndex(results['datetime'])
          results.drop(['datetime'], axis=1, inplace=True)
          results['open'] = results['open'].apply(makeFloat)
          results['high'] = results['high'].apply(makeFloat)
          results['low'] = results['low'].apply(makeFloat)
          results['close'] = results['close'].apply(makeFloat)
          results['volume'] = results['volume'].apply(makeInt)
          results['volume'].apply(lambda x: '%.12f' % x)
          print("Results for chart")
          results = results.iloc[::-1]
          print(results)

          buyPoints = []
          sellPoints = []

          counter = 0
          for i in range(0, len(results)):
               if counter == 0:
                    counter += 1
                    buyPoints.append(np.nan)
                    sellPoints.append(np.nan)
                    continue
               else:
                    if results.selector.iloc[i] == "BUY":
                         buyPoints.append(results.close.iloc[i] * 0.995)
                    else:
                         buyPoints.append(np.nan)
                    
                    if results.selector.iloc[i] == "SELL":
                         sellPoints.append(results.close.iloc[i] * 1.005)
                    else:
                         sellPoints.append(np.nan)

          # print(buyPoints)
          # print(sellPoints)
          # macd = results.ema12 - results.ema26
          macd = results['macd'].tolist()
          # sigval = results.macd.ewm(span=9).mean()
          sigval = results['sigval'].tolist()
          buyPoints = [None if i is np.nan else i for i in buyPoints]
          sellPoints = [None if i is np.nan else i for i in sellPoints]
          if any(isinstance(j, float) for j in buyPoints) and any(isinstance(i, float) for i in sellPoints):
               print("Both true")
               buyPoints = [np.nan if i is None else i for i in buyPoints]
               sellPoints = [np.nan if j is None else j for j in sellPoints]
               apds = [
                    mpf.make_addplot(buyPoints, type="scatter", markersize=120, marker="^"),
                    mpf.make_addplot(sellPoints, type="scatter", markersize=120, marker="v"),
                    mpf.make_addplot(macd, panel=1, color="fuchsia", secondary_y=False),
                    mpf.make_addplot(sigval, panel=1, color="b", secondary_y=False),
               ]
               print(f"{buyPoints} / {len(buyPoints)}")
               print(f"{sellPoints} / {len(sellPoints)}")
          else:
               if any(isinstance(j, float) for j in buyPoints) and not any(isinstance(i, float) for i in sellPoints):
                    print("List 1 true, list 2 false")
                    buyPoints = [np.nan if i is None else i for i in buyPoints]
                    apds = [
                         mpf.make_addplot(buyPoints, type="scatter", markersize=120, marker="^"),
                         mpf.make_addplot(macd, panel=1, color="fuchsia", secondary_y=False),
                         mpf.make_addplot(sigval, panel=1, color="b", secondary_y=False),
                    ]
                    print(f"{buyPoints} / {len(buyPoints)}")
               else:
                    print("List 2 true, list 1 false")
                    sellPoints = [np.NaN if j is None else j for j in sellPoints]
                    apds = [
                         mpf.make_addplot(sellPoints, type="scatter", markersize=120, marker="^"),
                         mpf.make_addplot(macd, panel=1, color="fuchsia", secondary_y=False),
                         mpf.make_addplot(sigval, panel=1, color="b", secondary_y=False),
                    ]
                    print(f"{sellPoints} / {len(sellPoints)}")
          mpf.plot(results,type='candle',addplot=apds,figscale=1.1,figratio=(8,5),title='\n'+ticker+' '+ timeframe, style='blueskies',panel_ratios=(6,3))
     except Exception as e:
          messagebox.showerror("ERROR", """There is currently no data for this stock timeframe pairing.\nPlease wait until the next interval before trying again.""")
          print(e)

# df['col1'] = df['col1'].apply(complex_function)
# Function to convert given datetime from US/New York timezone
# into local timezone (GMT/BST)
# Args
# datetime -> A value from the column that is given
def convertTimezone(timeInColumn):
     dt_utc = str(timeInColumn)
     dt_utc = dtInner.strptime(dt_utc, apiFormat)
     dt_utc = dt_utc.replace(tzinfo=from_zone)
     dt_local = dt_utc.astimezone(local_zone)
     local_time_str = dt_local.strftime(ukFormat)
     return local_time_str
     

# Function to calculate values and insert data into the table
# Args
# asset  -> Given name of the target asset, as a string
# period -> Given name of the target trading period, as a string
def calculateAndInsert(asset, period):
     try:
          # Install pymysql library as the MYSQL database
          pymysql.install_as_MySQLdb()
          # Create the engine using sqlalchemy
          engine = sqlalchemy.create_engine('mysql://root:beansontoastA1?@localhost:3306/stocktables')
          # Create query string to retrieve given asset, at timeframe, at set periods of 30 in JSON format
          querystring = {"symbol":asset,"interval":period,"outputsize":"30","format":"json"}
          # Using Python Requests GET method, make HTTP request to get the response from the API
          response = requests.request("GET", url, headers=headers, params=querystring)
          # Convert response to json
          jsonResponse = response.json()
          # Use built in Pandas function to normalize the json response into a dataframe
          df2 = json_normalize(jsonResponse, 'values')
          # print(tabulate(df2, showindex=False, headers=list(df2.columns)))
          # Drop unecessary columns -> removed for mplfinance to work
          # df2.drop(['open', 'high', 'low', 'volume'], axis=1, inplace=True)
          # Change index to datetime to be able to order by date
          # df2.set_index('datetime', inplace=True)
          # As data from the API comes earliest date first, in order to analyse it, it must be reversed
          df2 = df2.iloc[::-1]
          # print(df2.iloc[0])
          # Loop to find key from value name
          findKey = ""
          for key, value in indDict.items():
               if asset == value:
                    findKey = key
          # Set values according to standard MACD settings values by using build in pandas calculations rather than manual calculations for better accuracy and reduction of code
          df2['assetname'] = findKey
          df2['EMA12'] = df2.close.ewm(span=12).mean()
          df2['EMA26'] = df2.close.ewm(span=26).mean()
          df2['MACD'] = df2.EMA12 - df2.EMA26
          df2['sigval'] = df2.MACD.ewm(span=9).mean()
          df2['selector'] = ""

          # print("Before attempting conversion of timezones\nNo set index")
          # print(tabulate(df2, showindex=True, headers=list(df2.columns)))
          # df2['datetime'] = df2['datetime'].apply(convertTimezone)
          # df2['datetime'] = df2.apply(lambda x: convertTimezone(x['datetime']), axis=1)
          # df2['datetime'] = np.vectorize(convertTimezone)(df2['datetime'])

          print("No converting timezone, index reset before assigning selector, after calculations")
          df2.set_index('datetime', inplace=True)
          print(tabulate(df2, showindex=True, headers=list(df2.columns)))

          # Iterate through dataframe rows starting from index 1 (as 0 will have no value)
          for i in range(1, len(df2)):
               # print(f'MACD: {df2.MACD.iloc[i]}/, {type({df2.MACD.iloc[i]})}')
               # print(f'Sigval: {df2.sigval.iloc[i]}/, {type({df2.sigval.iloc[i]})}')

               if df2.MACD.iloc[i] > df2.sigval.iloc[i] and df2.MACD.iloc[i-1] < df2.sigval.iloc[i-1]:
                    df2.iloc[[i], 10] = 'BUY'
               elif df2.MACD.iloc[i] < df2.sigval.iloc[i] and df2.MACD.iloc[i-1] > df2.sigval.iloc[i-1]:
                    df2.iloc[[i], 10] = 'SELL'

          df2.to_sql((asset.lower()+period), engine, if_exists="append")
          # Try to remove any duplicates from the table (For some reason replace wont work)
          try:
               db = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    passwd="beansontoastA1?",
                    database="StockTables"
               )
               # Create cursor
               my_cursor = db.cursor()

               print("Removing duplicates if any exist from stocktables."+(asset+period).lower())

               # Execute query to delete duplicate records from the given table
               my_cursor.execute("""DELETE FROM stocktables.%s WHERE rowid NOT IN (SELECT * FROM (SELECT Max(rowid) FROM %s GROUP BY datetime, assetname, open, high, low, close, volume, selector) AS t);""" %((asset+period).lower(), (asset+period).lower()))

               # Commit changes to db
               db.commit()
          # Catch any exception and print for debugging
          except Exception as e:
               print(f'Exception inside delete duplicates: {e}')
          # Finally close the cursor and db to end function
          finally:
               my_cursor.close()
               db.close()
     # Catch any exceptions and print the traceback
     except Exception as e:
          print(f'Exception in calculate and insert: {e}')
          print(traceback.format_exc())

# Display new signals to board
def displayResults(dfOfSignals):
     try:
          # Query dataframe argument to select only signal records
          results = dfOfSignals.query('selector == "BUY" or selector == "SELL"')
          # Drop the rowid to compare with currentSignals
          # results = results.drop(['rowid'], axis=1, errors='ignore')
          results.sort_values(by=['datetime'])
          # Print results for checking
          print("Initial results")
          print(tabulate(results, showindex=False, headers=results.columns))
          # results = results.drop_duplicates(keep='first')
          # Make currentSignals global to allow it to be accessed as local in the function
          global currentSignals
          # Print 
          print("Current Signals dataframe")
          print(tabulate(currentSignals, showindex=False, headers=results.columns))
          results = results[~results.apply(tuple,1).isin(currentSignals.apply(tuple,1))]
          # if results[9] != "BUY" or results[9] != "SELL":
          #      results.shift(1, axis=1)
          print("Results after filter attempt")
          print(tabulate(results, showindex=False, headers=results.columns))
          currentSignals = pd.concat([results, currentSignals], ignore_index=True)
          print("Current signals after adding results")
          print(tabulate(currentSignals, showindex=False, headers=results.columns))
          # Trying to convert date format into local as string because MySQL only accepts
          # YYYY-MM-DD format, not the UK format
          print("Current signals after converting date format")
          results['datetime'] = results['datetime'].apply(convertTimezone)
          print(tabulate(results, showindex=True, headers=list(results.columns)))
          # Line 286 gives error signalDt = row[1] + time_delta
          results = results.sort_values(by=['datetime'])
          if not results.empty:
               print(tabulate(results, showindex=False, headers=results.columns))
               for row in results.itertuples():
                    if row[13] == "BUY":
                         displayBox.configure(state="normal")
                         assetName = row[3]
                         signalDt = row[2]
                         closePrice = row[7]
                         assetInputString = f'BUY: {assetName}\n'
                         displayBox.insert('end', assetInputString, 'BUY')
                         inputString = f"""Date/Time: {str(signalDt)}\nClose Price: {closePrice:.2f}\n---------------------------------------------\n"""
                         displayBox.insert('end', inputString)
                         print(inputString)
                    elif row[13] == "SELL":
                         displayBox.configure(state="normal")
                         assetName = row[3]
                         signalDt = row[2]
                         closePrice = row[7]
                         assetInputString = f'SELL: {assetName}\n'
                         displayBox.insert('end', assetInputString, 'SELL')
                         inputString = f"""Date/Time: {str(signalDt)}\nClose Price: {closePrice:.2f}\n---------------------------------------------\n"""
                         displayBox.insert('end', inputString)
                         print(inputString)
               displayBox.configure(state="disabled")
          else:
               print("Nothing available")
               displayBox.configure(state="normal")
               displayBox.insert('end', "Nothing to add")
               displayBox.configure(state="disabled")
     except Exception as e:
          print("DisplayBox error " + str(e))
          

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


# Establish Tkinter frame as root, set geometry, and resizable off
root = Tk()
root.title("Simple Stock Signal System")
root.geometry("650x600")
root.resizable(False, False)

# Initialize variables for dropdown boxes
clicked1   = StringVar(root)
clicked2   = StringVar(root)
clicked3   = StringVar(root)
clicked4   = StringVar(root)
clicked5   = StringVar(root)
timeFrame1 = StringVar(root)
timeFrame2 = StringVar(root)
timeFrame3 = StringVar(root)
timeFrame4 = StringVar(root)
timeFrame5 = StringVar(root)


# Function to synchronise timing with current time
def syncTiming5():
     # Get the current time as string
     now = str(dtInner.now())
     # Split string by colon
     splitNow = now.split(":")
     # Get minutes and seconds as ints from split list by typecasting
     minutes = int(splitNow[1])
     seconds = round(float(splitNow[2]))
     # Check if minutes is already a multiple of 5
     if minutes % 5 == 0:
          return 301
     else:
          min2 = minutes
          counter = 0
          while min2 % 5 != 0:
               min2 += 1
               counter += 1     
          actualSeconds = ((counter * 60) - seconds) + 1
          return(actualSeconds)

def syncTiming30():
     now = str(dtInner.now())
     splitNow = now.split(":")
     minutes = int(splitNow[1])
     seconds = round(float(splitNow[2]))
     if minutes == 30 or minutes == 0:
          return 1801
     else:
          if minutes < 30:
               diff = 30 - minutes
          else:
               diff = 59 - minutes
     actualSeconds = ((diff * 60) - seconds) + 1
     return(actualSeconds)

def syncTiming60():
     now = str(dtInner.now())
     splitNow = now.split(":")
     minutes = int(splitNow[1])
     seconds = round(float(splitNow[2]))
     if minutes == 30:
          return 3601
     else:
          if minutes < 30:
               diff = 30 - minutes
          else:
               diff = 59 - minutes
     actualSeconds = ((diff * 60) - seconds) + 1
     return(actualSeconds)


def getData(tf):
     apiArgTf = timeFrameDict[tf]
     print(tf, apiArgTf)
     symbolsToGet = []
     for key in srtCombo:
          if srtCombo[key][5] == tf:
               symbolsToGet.append(indDict[srtCombo[key][4]])
     print(symbolsToGet)
     for assetName in symbolsToGet:
          createTable(assetName, apiArgTf)
     for asset in symbolsToGet:
          try:
               calculateAndInsert(asset, apiArgTf)
               returnedDf = retrieveDataOneTf(symbolsToGet, apiArgTf)
               displayResults(returnedDf)
               # print(tabulate(returnedDf, showindex=False, headers=returnedDf.columns))
               # print(tabulate(df2, showindex=False, headers=list(df2.columns)))
          except Exception as e:
               print(f'There has been an error: {e}')
               print(traceback.format_exc())
          
# Define callback function
# Args
# clicker = The StringVar associated with the stock dropdown box
# timeframe = The StringVar associated with the timeframe 
# down box
# clickername = The name identifying the dropdown box being changed
def callback1(clicker, timeframe, clickerName):
     # When dropdown is changed, check if its combo exists
     # print(f'New clicker/timeframe combo: {clicker.get()}, {timeframe.get()}')
     for keyName in srtCombo:
          # print(f'Checking this clicker: {srtCombo[keyName]}')
          # print(f'Recieved clicker name: {clickerName}, Current key name: {keyName}')
          # print(f'{clicker.get()}, {timeframe.get()} vs {srtCombo[keyName][4]}, {srtCombo[keyName][5]}')
          if [clicker.get(), timeframe.get()] == [srtCombo[keyName][4], srtCombo[keyName][5]]:
               if clickerName == keyName:
                    continue
               else:
                    print(f'A duplicate has been found!')
                    messagebox.showinfo("ERROR", "You cannot have duplicate STOCK/TIMEFRAME combinations!")
                    if srtCombo[clickerName][1] == '':
                         clicker.set(srtCombo[clickerName][0])
                    else:
                         clicker.set(srtCombo[clickerName][1])
                    break
     else:
          # If combo does not exist, allow change and move stock pointers
          # Check if there is already a pointer in stock rotation
          if srtCombo[clickerName][1] == '':
               srtCombo[clickerName][1] = clicker.get()
               srtCombo[clickerName][4] = clicker.get()
          else:
               srtCombo[clickerName][0] = srtCombo[clickerName][1]
               srtCombo[clickerName][1] = clicker.get()
               srtCombo[clickerName][4] = clicker.get()
          print(f'drop variable has been changed to {clicker.get()}')
          print(f'New combo registered as {srtCombo[clickerName][4]}, {srtCombo[clickerName][5]}')


def callback2(clicker, timeframe, clickerName):
     # When dropdown is changed, check if its combo exists
     # print(f'New clicker/timeframe combo: {clicker.get()}, {timeframe.get()}')
     # clickerName = argname(clicker)
     for keyName in srtCombo:
          # print(f'Checking this clicker: {srtCombo[keyName]}')
          # print(f'Recieved clicker name: {clickerName}, Current key name: {keyName}')
          # print(f'{clicker.get()}, {timeframe.get()} vs {srtCombo[keyName][4]}, {srtCombo[keyName][5]}')
          if [clicker.get(), timeframe.get()] == [srtCombo[keyName][4], srtCombo[keyName][5]]:
               if clickerName == keyName:
                    continue
               else:
                    print(f'A duplicate time has been found!')
                    messagebox.showinfo("ERROR", "You cannot have duplicate STOCK/TIMEFRAME combinations!")
                    if srtCombo[clickerName][3] == '':
                         timeframe.set(srtCombo[clickerName][2])
                    else:
                         timeframe.set(srtCombo[clickerName][3])
                    break
     else:
          # If combo does not exist, allow change and move stock pointers
          # Check if there is already a pointer in stock rotation
          if srtCombo[clickerName][3] == '':
               srtCombo[clickerName][3] = timeframe.get()
               srtCombo[clickerName][5] = timeframe.get()
          else:
               srtCombo[clickerName][2] = srtCombo[clickerName][3]
               srtCombo[clickerName][3] = timeframe.get()
               srtCombo[clickerName][5] = timeframe.get()
               
          print(f'drop variable has been changed to {timeframe.get()}')
          print([clicker.get(), timeframe.get()])

     
def saveConfig():
     config_object = ConfigParser()
     config_object.read("config.ini")

     configData = config_object["STOCKCONFIG"]

     configData["stock1"] = clicked1.get()
     configData["time1"] = timeFrame1.get()

     configData["stock2"] = clicked2.get()
     configData["time2"] = timeFrame2.get()

     configData["stock3"] = clicked3.get()
     configData["time3"] = timeFrame3.get()

     configData["stock4"] = clicked4.get()
     configData["time4"] = timeFrame4.get()

     configData["stock5"] = clicked5.get()
     configData["time5"] = timeFrame5.get()

     with open('config.ini', 'w') as conf:
          config_object.write(conf)
     conf.close()
     print("Config written to!")

def loadConfig():
     config_object = ConfigParser()
     config_object.read("config.ini")

     configData = config_object["STOCKCONFIG"]
     clicked1.set(configData["stock1"])
     timeFrame1.set(configData["time1"])

     clicked2.set(configData["stock2"])
     timeFrame2.set(configData["time2"])

     clicked3.set(configData["stock3"])
     timeFrame3.set(configData["time3"])

     clicked4.set(configData["stock4"])
     timeFrame4.set(configData["time4"])

     clicked5.set(configData["stock5"])
     timeFrame5.set(configData["time5"])
     print("Config loaded!")

# Stock 1
#####################################
clicked1.set(stockNameList[0])
timeFrame1.set(timeFrames[0])
srtCombo["clicked1"][0] = clicked1.get()
srtCombo["clicked1"][2] = timeFrame1.get()
srtCombo["clicked1"][4] = clicked1.get()
srtCombo["clicked1"][5] = timeFrame1.get()
clicked1.trace_add("write", lambda var_name, var_index, operation: callback1(clicked1, timeFrame1, "clicked1"))
timeFrame1.trace_add("write", lambda var_name, var_index, operation: callback2(clicked1, timeFrame1, "clicked1"))

#####################################

# Stock 2
#####################################
clicked2.set(stockNameList[1])
timeFrame2.set(timeFrames[0])
srtCombo["clicked2"][0] = clicked2.get()
srtCombo["clicked2"][2] = timeFrame2.get()
srtCombo["clicked2"][4] = clicked2.get()
srtCombo["clicked2"][5] = timeFrame2.get()
clicked2.trace_add("write", lambda var_name, var_index, operation: callback1(clicked2, timeFrame2, "clicked2"))
timeFrame2.trace_add("write", lambda var_name, var_index, operation: callback2(clicked2, timeFrame2, "clicked2"))
#####################################

# Stock 3
#####################################
clicked3.set(stockNameList[2])
timeFrame3.set(timeFrames[0])
srtCombo["clicked3"][0] = clicked3.get()
srtCombo["clicked3"][2] = timeFrame3.get()
srtCombo["clicked3"][4] = clicked3.get()
srtCombo["clicked3"][5] = timeFrame3.get()
clicked3.trace_add("write", lambda var_name, var_index, operation: callback1(clicked3, timeFrame3, "clicked3"))
timeFrame3.trace_add("write", lambda var_name, var_index, operation: callback2(clicked3, timeFrame3, "clicked3"))
#####################################

# Stock 4
#####################################
clicked4.set(stockNameList[3])
timeFrame4.set(timeFrames[0])
srtCombo["clicked4"][0] = clicked4.get()
srtCombo["clicked4"][2] = timeFrame4.get()
srtCombo["clicked4"][4] = clicked4.get()
srtCombo["clicked4"][5] = timeFrame4.get()
clicked4.trace_add("write", lambda var_name, var_index, operation: callback1(clicked4, timeFrame4, "clicked4"))
timeFrame4.trace_add("write", lambda var_name, var_index, operation: callback2(clicked4, timeFrame4, "clicked4"))
#####################################

# Stock 5
#####################################
clicked5.set(stockNameList[4])
timeFrame5.set(timeFrames[0])
srtCombo["clicked5"][0] = clicked5.get()
srtCombo["clicked5"][2] = timeFrame5.get()
srtCombo["clicked5"][4] = clicked5.get()
srtCombo["clicked5"][5] = timeFrame5.get()
clicked5.trace_add("write", lambda var_name, var_index, operation : callback1(clicked5, timeFrame5, "clicked5"))
timeFrame5.trace_add("write", lambda var_name, var_index, operation: callback2(clicked5, timeFrame5, "clicked5"))
#####################################
stockNameList
drop1 = OptionMenu(root, clicked1, *stockNameList)
drop1.config(width=25, bg="green", foreground="white")
drop1.place(x=0, y=0)

button1 = Button(root, text="Get chart")
button1.columnconfigure(0, weight=0)
button1.place(x=0, y=35)
button1['command'] = lambda:displayChartWithSignals(clicked1.get(), timeFrame1.get()) 

dropTf1 = OptionMenu(root, timeFrame1, *timeFrames)
dropTf1.config(width=10, bg="blue", foreground="white")
dropTf1.place(x=90, y=32)

########################################################

drop2 = OptionMenu(root, clicked2, *stockNameList)
drop2.config(width=25, bg="green", foreground="white")
drop2.place(x=0, y=80)

button2 = Button(root, text="Get chart")
button2.columnconfigure(0, weight=0)
button2.place(x=0, y=115)
button2['command'] = lambda:displayChartWithSignals(clicked2.get(), timeFrame2.get()) 

dropTf2 = OptionMenu(root, timeFrame2, *timeFrames)
dropTf2.config(width=10, bg="blue", foreground="white")
dropTf2.place(x=90, y=112)

#######################################################

drop3 = OptionMenu(root, clicked3, *stockNameList)
drop3.config(width=25, bg="green", foreground="white")
drop3.place(x=0, y=160)

button3 = Button(root, text="Get chart")
button3.columnconfigure(0, weight=0)
button3.place(x=0, y=195)
button3['command'] = lambda:displayChartWithSignals(clicked3.get(), timeFrame3.get()) 

dropTf3 = OptionMenu(root, timeFrame3, *timeFrames)
dropTf3.config(width=10, bg="blue", foreground="white")
dropTf3.place(x=90, y=192)

#######################################################

drop4 = OptionMenu(root, clicked4, *stockNameList)
drop4.config(width=25, bg="green", foreground="white")
drop4.place(x=0, y=240)

button4 = Button(root, text="Get chart")
button4.columnconfigure(0, weight=0)
button4.place(x=0, y=275)
button4['command'] = lambda:displayChartWithSignals(clicked4.get(), timeFrame4.get())

dropTf4 = OptionMenu(root, timeFrame4, *timeFrames)
dropTf4.config(width=10, bg="blue", foreground="white")
dropTf4.place(x=90, y=272)

########################################################

drop5 = OptionMenu(root, clicked5, *stockNameList)
drop5.config(width=25, bg="green", foreground="white")
drop5.place(x=0, y=320)

button5 = Button(root, text="Get chart")
button5.columnconfigure(0, weight=0)
button5.place(x=0, y=355)
button5['command'] = lambda:displayChartWithSignals(clicked5.get(), timeFrame5.get()) 

dropTf5 = OptionMenu(root, timeFrame5, *timeFrames)
dropTf5.config(width=10, bg="blue", foreground="white")
dropTf5.place(x=90, y=352)

########################################################

saveConfig = Button(root, text="Save Selections", command=saveConfig)
saveConfig.config(width=15, bg="white", foreground="black")
saveConfig.place(x=440, y=570)

loadConfig = Button(root, text="Load Selections", command=loadConfig)
loadConfig.config(width=15, bg="white", foreground="black")
loadConfig.place(x=320, y=570)

exitButton = Button(root, text="Exit", command=root.destroy)
exitButton.config(width=10, bg="red", foreground="white")
exitButton.place(x=560, y=570)

########################################################

displayBox = st.ScrolledText(root, width=29, height=23, font=("Calibri", 15))
displayBox.place(x=300, y=2)
displayBox.tag_configure('BUY', background='black', foreground='lime')
displayBox.tag_configure('SELL', background='black', foreground='red')
displayBox.configure(state="disabled")


fiveMinSyncTime = syncTiming5()
thirtyMinSyncTime = syncTiming30()
hourSyncTime = syncTiming60()

print(f'Five mins in: {fiveMinSyncTime} seconds')
print(f'Thirty mins in: {thirtyMinSyncTime} seconds ')
print(f'One hour in: {hourSyncTime} seconds')

_5minThread = RepeatedTimer(fiveMinSyncTime, getData, "5MIN")
_30minThread = RepeatedTimer(thirtyMinSyncTime, getData, "30MIN")
_1hThread = RepeatedTimer(hourSyncTime, getData, "1HOUR")

_5minThread.interval = 301
_30minThread.interval = 1801
_1hThread.interval = 3601

# Begin Tkinter GUI event loop
root.mainloop()

# Stop timer threads after GUI exection ends
# Otherwise threads will cause program to continue to run
_5minThread.stop()
_30minThread.stop()
_1hThread.stop()