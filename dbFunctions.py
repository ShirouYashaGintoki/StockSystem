# Import required modules
import mysql.connector
import pymysql
import pandas as pd
import sqlalchemy
from pandas import json_normalize
from tkinter import messagebox
from tabulate import tabulate
import requests
from configparser import ConfigParser

# Load database and API config files
config_object = ConfigParser()
config_object.read("config.ini")
dbInfo = config_object["DATABASE"]
apiInfo = config_object["API"]

# Indices as dataframe, Sheet 1 is main sheet, Sheet 2 has 5 for testing
indices = pd.read_excel('tickers.xlsx', sheet_name='Sheet 1')
# Create a dictionary of stock names and their ticker symbols
indDict = pd.Series(indices.Symbol.values, index=indices.CompanyName).to_dict()

# Function to find asset name from its ticker
# Args
# ticker = Symbol as a string of the ticker to find the name for
def findNameFromTicker(ticker):
     # Set findkey to blank value as placeholder
     findKey = ""
     # Loop through dictionary of asset names and symbols
     for key, value in indDict.items():
          # If given ticker matches value
          if ticker == value:
               # Set findkey to the key, which is the name of the asset
               findKey = key
     # Return result
     return findKey

# Function to create a table in the database
# for a given asset and timeframe combination
# Args
# assetName = Given name of asset as string
# timeFrame = Given time frame as string
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

# Function to retrieve data for a list of assets in one time frame
# Args
# listOfAssets = List of assets for which data is to be retrieved
# timeframe = The timeframe for which the data is to be retrieved
def retrieveDataOneTf(listOfAssets, timeframe):
     # Install pymysql as MySQL
     pymysql.install_as_MySQLdb()
     # Create sqlalchemy engine using link from config
     engine = sqlalchemy.create_engine(dbInfo["dblink"])
     # Create list to store dataframes
     listOfFrames = []
     # Loop through assets in given list
     # Query the last 30 results and order by descending datetime
     for asset in listOfAssets:
          query = f'''
          SELECT *
          FROM {asset+timeframe}
          ORDER BY datetime DESC LIMIT 30;'''
          df = pd.read_sql(query, engine)
          # Append to list of frames
          listOfFrames.append(df)
     # Return concatenated list into one dataframe
     return pd.concat(listOfFrames)

# Initialize API headers
headers = {
     'x-rapidapi-host' : apiInfo["apiheader"],
     'x-rapidapi-key': apiInfo["apikey"]
}

# Function to calculate values and insert data into the table
# Args
# asset  = Given name of the target asset, as a string
# period = Given name of the target trading period, as a string
def calculateAndInsert(asset, period):
     try:
          # Install pymysql library as the MYSQL database
          pymysql.install_as_MySQLdb()
          # Create the engine using sqlalchemy
          engine = sqlalchemy.create_engine(dbInfo["dblink"])
          # Create query string to retrieve given asset, at timeframe, at set output size of 30 in JSON format
          querystring = {"symbol":asset,"interval":period,"outputsize":"30","format":"json"}
          # Using Python Requests GET method, make HTTP request to get the response from the API
          response = requests.request("GET", apiInfo["url"], headers=headers, params=querystring)
          # Convert response to json
          jsonResponse = response.json()
          # Use built in Pandas function to normalize the json response into a dataframe
          df2 = json_normalize(jsonResponse, 'values')
          # As data from the API comes earliest date first, in order to analyse it, it must be reversed
          df2 = df2.iloc[::-1]
          # Set values according to standard MACD settings values by using build in pandas calculations rather than manual calculations for better accuracy and reduction of code
          df2['assetname'] = findNameFromTicker(asset)
          df2['EMA12'] = df2.close.ewm(span=12).mean()
          df2['EMA26'] = df2.close.ewm(span=26).mean()
          df2['MACD'] = df2.EMA12 - df2.EMA26
          df2['sigval'] = df2.MACD.ewm(span=9).mean()
          # Keep selector blank to hold the value of a signal if there is one
          df2['selector'] = ""
          # Set index to the datetime column
          df2.set_index('datetime', inplace=True)
          # Iterate through dataframe rows starting from index 1 (as 0 will have no value)
          for i in range(1, len(df2)):
               # Check if a buy crossover has occurred
               if df2.MACD.iloc[i] > df2.sigval.iloc[i] and df2.MACD.iloc[i-1] < df2.sigval.iloc[i-1]:
                    # Then set the selector column to "BUY" for this record
                    df2.iloc[[i], 10] = 'BUY'
               # Elif a sell crossover occurred
               elif df2.MACD.iloc[i] < df2.sigval.iloc[i] and df2.MACD.iloc[i-1] > df2.sigval.iloc[i-1]:
                    # Set selector to sell for this record
                    df2.iloc[[i], 10] = 'SELL'
          # Add results to database
          df2.to_sql((asset.lower()+period), engine, if_exists="append")
          # Try to connect to database
          try:
               db = mysql.connector.connect(
                    host=dbInfo['host'],
                    user=dbInfo['user'],
                    passwd=dbInfo['password'],
                    database=dbInfo['dbname']
               )
               # Create cursor
               my_cursor = db.cursor()

               print("Removing duplicates if any exist from stocktables."+(asset+period).lower())

               # Execute query to delete duplicate records from the given table by subquerying the table and selecting the highest rowid (primary key) records, grouping by their columns. Then using that subquery to delete whatever remainder records are not in that query, leaving unique records with the highest rowid
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
     # Catch any exception with connecting to the API, print for debugging and quit application
     except Exception as e:
          print(f'Exception in calculate and insert: {e}')
          messagebox.showinfo("ERROR", "There has been an issue connecting to the API, please try again later\nThis application will now close")
          exit()