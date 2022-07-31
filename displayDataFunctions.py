# Import required modules
import pymysql
import sqlalchemy
import pandas as pd
import numpy as np
from tkinter import messagebox
import mplfinance as mpf
from configparser import ConfigParser
from tabulate import tabulate
import datetime as dtOuter
from datetime import datetime as dtInner
from dateutil import tz
import yfinance as yf
from dbFunctions import retrieveDataOneTf

# Create config object to access database
config_object = ConfigParser()
config_object.read("config.ini")
dbInfo = config_object["DATABASE"]

# Create local timeframe dictionary to hold API equivalents
timeFrameDict = {
     "5MIN" : "5min",
     "30MIN" : "30min",
     "1HOUR" : "1h"
}

# Indices as dataframe, Sheet 1 is main sheet, Sheet 2 has 5 for testing
indices = pd.read_excel('tickers.xlsx', sheet_name='Sheet 1')
# Create a dictionary of stock names and their ticker symbols
indDict = pd.Series(indices.Symbol.values, index=indices.CompanyName).to_dict()
# Create a list of stock names for display purposes
tickerSymbolList = sorted(list(indDict.values()))

# Set time zones and formats as data received is in US timezone
from_zone = tz.gettz('America/New_York')
apiFormat = "%Y-%m-%d %H:%M:%S"
ukFormat = "%d-%m-%Y %H:%M:%S"
local_zone = tz.tzlocal()

# Dataframe to hold the records of the current signals to prevent duplicate signals
currentSignals = pd.DataFrame(columns=["datetime", "assetname", "open", "high", "low", "close", "volume", "ema12", "ema26", "macd", "sigval", "selector"])

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

# Function to convert given datetime from US/New York timezone
# into local timezone (GMT/BST)
# Args
# timeInColumn = A timestamp that is given from a column
def convertTimezone(timeInColumn):
     # Convert UTC datetime to strig
     dt_utc = str(timeInColumn)
     # Produce datetime object in the same format received in the API
     dt_utc = dtInner.strptime(dt_utc, apiFormat)
     # Use replace to format the datetime in the US time format
     dt_utc = dt_utc.replace(tzinfo=from_zone)
     # Create local time by using timezone library to convert UTC datetime to local timezone
     dt_local = dt_utc.astimezone(local_zone)
     # Use strftime to convert the datetime object to a string in the UK time format 
     local_time_str = dt_local.strftime(ukFormat)
     # Return result
     return local_time_str

# Function to convert given result into a float datatype
# Args
# given = Given value to be converted to a float
def makeFloat(given):
     # Set fixed to given argument typecasted as float
     fixed = float(given)
     # Return result
     return fixed

# Function to convert given result into an int datatype
# Args
# given = Given value to be converted to an int
def makeInt(given):
     # Set fixed to given argument typecasted as an int
     fixed = int(given)
     # Return result
     return fixed

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

# Function to display chart with signal indicators
# ticker = Given ticker
# timeframe = Given timeframe
def displayChartWithSignals(ticker, timeframe):
     try:
          # Get API argument equivalent of timeframe
          accessTf = timeFrameDict[timeframe]
          # Retrieve last 30 results from the database
          results = retrieveDataOneTf([indDict[ticker]], accessTf)
          # Set index to datetime as datetimeindex for mplfinance
          results.index = pd.DatetimeIndex(results['datetime'])
          # Drop remaining datetime column as it's not needed
          results.drop(['datetime'], axis=1, inplace=True)
          # Convert open, high, low, close to floats, and volume to int
          results['open'] = results['open'].apply(makeFloat)
          results['high'] = results['high'].apply(makeFloat)
          results['low'] = results['low'].apply(makeFloat)
          results['close'] = results['close'].apply(makeFloat)
          results['volume'] = results['volume'].apply(makeInt)
          print("Results for chart")
          # Reverse results so later results are first
          results = results.iloc[::-1]
          print(results)

          # Create lists to hold buy and sell points
          buyPoints = []
          sellPoints = []

          # Set counter to append nans on first iteration as it won't have any result
          # As it is skipped in the calculation phase
          counter = 0
          # Loop through range from 0, to length of results
          for i in range(0, len(results)):
               # If it's the first iteration
               if counter == 0:
                    # Increment counter so this doesn't activate again
                    counter += 1
                    # Append None to the lists to represent no signal
                    buyPoints.append(None)
                    sellPoints.append(None)
                    # Continue the loop
                    continue
               # Else if check if there is a signal in that record
               else:
                    if results.selector.iloc[i] == "BUY":
                         # Multiply the resulting close price in that record by a small amount to make the marker appear below the candle
                         buyPoints.append(results.close.iloc[i] * 0.995)
                    else:
                         # Else append None for no signal in the record
                         buyPoints.append(None)
                    
                    # Repeat same as above if there is a sell signal in that record
                    if results.selector.iloc[i] == "SELL":
                         sellPoints.append(results.close.iloc[i] * 1.005)
                    else:
                         sellPoints.append(None)

          # Convert MACD and signal value results to lists to provide to mplfinance
          macd = results['macd'].tolist()
          sigval = results['sigval'].tolist()
          # Check if buyPoints and sellPoints have floats in them (to represent signals)
          if any(isinstance(j, float) for j in buyPoints) and any(isinstance(i, float) for i in sellPoints):
               print("Both true")
               # Convert any Nones to np.nan as floating values are required by mplfinance
               buyPoints = [np.nan if i is None else i for i in buyPoints]
               sellPoints = [np.nan if j is None else j for j in sellPoints]
               # Add markers for buy and sell signals
               apds = [
                    mpf.make_addplot(buyPoints, type="scatter", markersize=120, marker="^"),
                    mpf.make_addplot(sellPoints, type="scatter", markersize=120, marker="v"),
                    mpf.make_addplot(macd, panel=1, color="fuchsia", secondary_y=False),
                    mpf.make_addplot(sigval, panel=1, color="b", secondary_y=False),
               ]
               print(f"{buyPoints} / {len(buyPoints)}")
               print(f"{sellPoints} / {len(sellPoints)}")
          # Else if there are not both buy and sell signals
          else:
               # Check if only buyPoints has signals in it
               if any(isinstance(j, float) for j in buyPoints) and not any(isinstance(i, float) for i in sellPoints):
                    print("List 1 true, list 2 false")
                    # Replace any Nones with nans
                    buyPoints = [np.nan if i is None else i for i in buyPoints]
                    # Add only buyPoints to markers
                    apds = [
                         mpf.make_addplot(buyPoints, type="scatter", markersize=120, marker="^"),
                         mpf.make_addplot(macd, panel=1, color="fuchsia", secondary_y=False),
                         mpf.make_addplot(sigval, panel=1, color="b", secondary_y=False),
                    ]
                    print(f"{buyPoints} / {len(buyPoints)}")
               # Repeat as above but for sell signals and not buy signals
               elif any(isinstance(j, float) for j in sellPoints) and not any(isinstance(i, float) for i in buyPoints):
                    print("List 2 true, list 1 false")
                    sellPoints = [np.NaN if j is None else j for j in sellPoints]
                    apds = [
                         mpf.make_addplot(sellPoints, type="scatter", markersize=120, marker="^"),
                         mpf.make_addplot(macd, panel=1, color="fuchsia", secondary_y=False),
                         mpf.make_addplot(sigval, panel=1, color="b", secondary_y=False),
                    ]
                    print(f"{sellPoints} / {len(sellPoints)}")
               # If there are no signals at all, just show the chart
               else:
                    print("No signals, displaying normal chart")
                    apds = [
                         mpf.make_addplot(macd, panel=1, color="fuchsia", secondary_y=False),
                         mpf.make_addplot(sigval, panel=1, color="b", secondary_y=False),
                    ]
          # Finally plot the candlestick chart
          mpf.plot(results,type='candle',addplot=apds,figscale=1.1,figratio=(8,5),title='\n'+ticker+' '+ timeframe, style='blueskies',panel_ratios=(6,3))
     # Catch an exception of no data, and show error to user
     except Exception as e:
          messagebox.showerror("ERROR", """There is currently no data for this stock timeframe pairing.\nPlease wait until the next interval before trying again.""")
          print(e)

# Display new signals to board
def displayChart(dfOfSignals, displayBox):
     try:
          # Query dataframe argument to select only signal records
          results = dfOfSignals.query('selector == "BUY" or selector == "SELL"')
          # Sort the values by datetime
          results.sort_values(by=['datetime'])
          # Print results for checking
          print("Initial results")
          print(tabulate(results, showindex=False, headers=results.columns))
          # Make currentSignals global to allow it to be accessed as local in the function
          global currentSignals
          print("Current Signals dataframe")
          print(tabulate(currentSignals, showindex=False, headers=results.columns))
          # Reassign results to filter duplicate signals that have already been shown
          results = results[~results.apply(tuple,1).isin(currentSignals.apply(tuple,1))]
          print("Results after filter attempt")
          print(tabulate(results, showindex=False, headers=results.columns))
          # Update signals shown so far by adding results to currentsignals
          currentSignals = pd.concat([results, currentSignals], ignore_index=True)
          print("Current signals after adding results")
          print(tabulate(currentSignals, showindex=False, headers=results.columns))
          print("Current signals after converting date format")
          # Convert the date format to UK by applying the convertTimezone function to datetime column
          results['datetime'] = results['datetime'].apply(convertTimezone)
          print(tabulate(results, showindex=True, headers=list(results.columns)))
          # Re-sort results by datetime
          results = results.sort_values(by=['datetime'])
          # Ensure results is not empty
          signalsPosted = False
          if not results.empty:
               print("Results sorted by datetime")
               print(tabulate(results, showindex=False, headers=results.columns))
               # Iterate through each row in results
               for row in results.itertuples():
                    # If the signal is BUY
                    if row[13] == "BUY":
                         # Set displaybox state to normal so text can be input
                         displayBox.configure(state="normal")
                         # Set assetname, datetime and close price
                         assetName = row[3]
                         signalDt = row[2]
                         closePrice = row[7]
                         # Insert the formatted string with "BUY" tag so it highlights the text
                         assetInputString = f'BUY: {assetName}\n'
                         displayBox.insert('end', assetInputString, 'BUY')
                         inputString = f"""Date/Time: {str(signalDt)}\nClose Price: {closePrice:.2f}\n---------------------------------------------\n"""
                         displayBox.insert('end', inputString)
                         print(inputString)
                    elif row[13] == "SELL":
                         # Repeat for sell
                         displayBox.configure(state="normal")
                         assetName = row[3]
                         signalDt = row[2]
                         closePrice = row[7]
                         assetInputString = f'SELL: {assetName}\n'
                         displayBox.insert('end', assetInputString, 'SELL')
                         inputString = f"""Date/Time: {str(signalDt)}\nClose Price: {closePrice:.2f}\n---------------------------------------------\n"""
                         displayBox.insert('end', inputString)
                         print(inputString)
                    signalsPosted = True
               # Finally, set the state back to disabled so the user can't edit it
               displayBox.configure(state="disabled")
               return signalsPosted
          else:
               # Else, print to the console for debugging, no need to display anything to the box
               print("Nothing available")
               return signalsPosted
     # Catch any exception and print for debugging
     except Exception as e:
          print("DisplayBox error " + str(e))

# Function to get the top 5 winners/losers by pct change from the last day
# Args
# top5Box = The text box to display top 5
# bot5Box = The text box to display worst 5
def getRecentDayPctDiff(top5Box, bot5Box):
     # Get current datetime
     tod = dtInner.now()
     # Set d to the value of 7 days
     d = dtOuter.timedelta(days = 7)
     # Subtract from today to go back 1 week
     a = tod - d
     # Get start and end dates as strings using strftime
     start = a.strftime("%Y-%m-%d")
     end = tod.strftime("%Y-%m-%d")
     # Create list of frames
     listOfFrames = []
     # For each symbol in the list of symbols
     for tickerSymbol in tickerSymbolList:
          # Create a temporary dataframe with symbol and percentage change
          df = pd.DataFrame(columns=["Symbol", "Percentage Change (%)"])
          # If the symbol is BRK.A, convert it to BRK-A due to yfinance differences
          if tickerSymbol == "BRK.A": tickerSymbol = "BRK-A"
          # Get yfinance ticker object of the symbol
          tick = yf.Ticker(tickerSymbol)
          # Get the history in the period of 5 days in 1 day intervals
          tickerHistory = tick.history(period='5d', interval='1d', start=start, end=end, auto_adjust=False, rounding=True)
          # Reverse the order
          tickerHistory = tickerHistory.iloc[::-1]
          # Drop the unecessary columns
          tickerHistory.drop(['Dividends', 'Adj Close', 'Stock Splits'], axis=1, inplace=True, errors="ignore")
          # Take the 2 most recent results
          tickerHistory = tickerHistory.head(2)

          # Create variables to hold the close values
          day1Close = tickerHistory.Close.iloc[0]
          day2Close = tickerHistory.Close.iloc[1]

          # Calculate the percentage difference
          percent_diff = (((float(day1Close) - float(day2Close))/float(day2Close)) * 100)
          # Add it to the end of the dataframe
          df.loc[-1] = [tickerSymbol, percent_diff]
          # Format the percentage change to 2 decimal points
          df["Percentage Change (%)"].apply(lambda x: '%.2f' % x)
          # Append the resulting dataframe to list of frames
          listOfFrames.append(df)
     # Concatenate all the frames into one 
     result = pd.concat(listOfFrames)
     # Sort the values by percentage change
     result = result.sort_values(by=["Percentage Change (%)"], ascending=False)
     # Get the top 5
     top5 = result.head(5)
     # Get the worst 5
     bot5 = result.tail(5)
     # Reverse order of the worst 5 so the lowest is at the top
     bot5 = bot5.iloc[::-1]
     # Create placeholder prefix string variable
     prefix = ""
     # Configure the text boxes so that they are editable
     top5Box.configure(state="normal")
     bot5Box.configure(state="normal")
     # Delete whatever was previously there
     top5Box.delete('1.0', "end")
     bot5Box.delete('1.0', "end")
     # Loop through the rows in top 5
     for row in top5.itertuples():
          # If the percentage change is larger than 0, add a +, otherwise leave it as it will set itself to negative
          prefix = "+" if row[2] > 0 else ""
          # Create formatted string to insert text
          insertText = f'Asset: {findNameFromTicker(row[1])} | Pct Change: {prefix}{row[2]:.2f}%\n'
          # Insert the text
          top5Box.insert("end", insertText)
          print(f'Asset: {findNameFromTicker(row[1])} | Pct Change: {prefix}{row[2]:.2f}%')
     # Repeat for worst 5
     for row in bot5.itertuples():
          prefix = "+" if row[2] > 0 else ""
          insertText = f'Asset: {findNameFromTicker(row[1])} | Pct Change: {prefix}{row[2]:.2f}%\n'
          bot5Box.insert("end", insertText)
          print(f'Asset: {findNameFromTicker(row[1])} | Pct Change: {prefix}{row[2]:.2f}%')
     # Configure the boxes back to disabled
     top5Box.configure(state="disabled")
     bot5Box.configure(state="disabled")