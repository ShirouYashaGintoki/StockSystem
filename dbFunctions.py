import mysql.connector
import pymysql
import pandas as pd
import sqlalchemy
from pandas import json_normalize
from tkinter import messagebox
from tabulate import tabulate
import requests
from configparser import ConfigParser
from displayDataFunctions import findNameFromTicker

config_object = ConfigParser()
config_object.read("config.ini")
dbInfo = config_object["DATABASE"]
apiInfo = config_object["API"]

# Indices as dataframe, Sheet 1 is main sheet, Sheet 2 has 5 for testing
indices = pd.read_excel('tickers.xlsx', sheet_name='Sheet 1')
# Create a dictionary of stock names and their ticker symbols
indDict = pd.Series(indices.Symbol.values, index=indices.CompanyName).to_dict()

# Function to create a table in the database
# for a given asset and timeframe combination
# Args
# assetName -> Given name of asset as string
# timeFrame -> Given time frame as string
def createTable(assetName, timeFrame):
     # Try to establish connection to db schema
     try:
          db = mysql.connector.connect(
               host=dbInfo['host'],
               user=dbInfo['user'],
               passwd=dbInfo['password'],
               database=dbInfo['dbname']
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

def retrieveDataOneTf(listOfAssets, timeframe):
     pymysql.install_as_MySQLdb()
     engine = sqlalchemy.create_engine(dbInfo["dblink"])
     listOfFrames = []
     for asset in listOfAssets:
          query = f'''
          SELECT *
          FROM {asset+timeframe}
          ORDER BY datetime DESC LIMIT 30;'''
          df = pd.read_sql(query, engine)
          listOfFrames.append(df)
     return pd.concat(listOfFrames)

headers = {
     'x-rapidapi-host' : apiInfo["apiheader"],
     'x-rapidapi-key': apiInfo["apikey"]
}

# Function to calculate values and insert data into the table
# Args
# asset  -> Given name of the target asset, as a string
# period -> Given name of the target trading period, as a string
def calculateAndInsert(asset, period):
     try:
          # Install pymysql library as the MYSQL database
          pymysql.install_as_MySQLdb()
          # Create the engine using sqlalchemy
          engine = sqlalchemy.create_engine(dbInfo["dblink"])
          # Create query string to retrieve given asset, at timeframe, at set periods of 30 in JSON format
          querystring = {"symbol":asset,"interval":period,"outputsize":"30","format":"json"}
          # Using Python Requests GET method, make HTTP request to get the response from the API
          response = requests.request("GET", apiInfo["url"], headers=headers, params=querystring)
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
          # findKey = ""
          # for key, value in indDict.items():
          #      if asset == value:
          #           findKey = key
          # Set values according to standard MACD settings values by using build in pandas calculations rather than manual calculations for better accuracy and reduction of code
          df2['assetname'] = findNameFromTicker(asset)
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
          messagebox.showinfo("ERROR", "There has been an issue connecting to the API, please try again later\nThis application will now close")
          exit()