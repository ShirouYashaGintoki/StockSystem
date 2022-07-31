# Import required libraries
from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext as st
import pandas as pd
import threading
import time
import mysql.connector
from configparser import ConfigParser
from configSetup import ftConfigSetup
from timing import syncTiming5, syncTiming30, syncTiming60
from playsound import playsound

# Try to open config file to check if it exists
try:
     # If it exists, just close it as we now know it exists
     with open("config.ini") as cfg:
          print("Config found!")
          cfg.close()
# If it doesn't exist
except Exception as e:
     # Create a local config file and print to console for debugging
     print("Config not found")
     ftConfigSetup()
     print("Config created!")

# Import from other modules that require the config to exist before importing
from displayDataFunctions import displayChartWithSignals, displayChart, getRecentDayPctDiff
from dbFunctions import retrieveDataOneTf, createTable, calculateAndInsert

# Create config parser object to read config file
config_object = ConfigParser()
# Read config file
config_object.read("config.ini")
# Set up 2 global config objects are needed throughout this file
# dbInfo for database related information (host, dbname etc)
dbInfo = config_object["DATABASE"]
# stockTfInfo for ticker/timeframe combinations
stockTfInfo = config_object["STOCKCONFIG"]

# Indices as dataframe from excel spreadsheet
indices = pd.read_excel('tickers.xlsx', sheet_name='Sheet 1')
# Create a dictionary of stock names and their ticker symbols
indDict = pd.Series(indices.Symbol.values, index=indices.CompanyName).to_dict()
# Create a list of stock names for display purposes
stockNameList = sorted(list(indDict.keys()))

# List of timeframes, to be changed to 5min, 30min, 1h
# 1h is HH:00
# 30min is either HH:00 or HH:30
# 5min has anything that is a multiple of 5 or HH:00
timeFrames = ['5MIN', '30MIN', '1HOUR']

# Dictionary to hold the equivalents of timeframes and API request arguments
timeFrameDict = {
     "5MIN" : "5min",
     "30MIN" : "30min",
     "1HOUR" : "1h"
}

# Dictionary to handle rotation of stock, time
# and the current stock/time combination
# Indexes 0 for last, 1 for new stock rotation
# Indexes 2 for last, 3 for new time rotation
# Indexes 4, 5 to store the current stock time combination
srtCombo = {
     "clicked1" : ['', '', '', '', '', ''],
     "clicked2" : ['', '', '', '', '', ''],
     "clicked3" : ['', '', '', '', '', ''],
     "clicked4" : ['', '', '', '', '', ''],
     "clicked5" : ['', '', '', '', '', '']
}

# Try to connect to the database
try: 
     # Connect using mysql connector with details from config
     db = mysql.connector.connect(
     host=dbInfo['host'],
     user=dbInfo['user'],
     passwd=dbInfo['password']
     )
# Catch any errors if can't connect to the database
except Exception as e:
     print(e)
     # Display error box to user and quit
     messagebox.showinfo("ERROR", "There was a problem connecting to the database.\nPlease try again later\nThis application will now close")
     exit()

# Create cursor
my_cursor = db.cursor()

# Try to create database schema, catch exception if fails
try:
     my_cursor.execute("CREATE DATABASE StockTables")
except Exception:
     print("DB schema already exists")

# Close database connection now
db.close()

# Class found on stackoverflow by eraoul
# https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds
# Create class for repeated timer
class RepeatedTimer():
     # Class initialization function
     # Args
     # interval = Given interval until next function call
     # function = Function to call once interval is reached
     def __init__(self, interval, function, *args):
          self._timer = None
          self.interval = interval
          self.function = function
          self.args = args
          self.is_running = False
          self.next_call = time.time()
          self.start()

     # Function to run repeated timer
     def _run(self):
          # Set running to false
          self.is_running = False
          # Start repeated timer
          self.start()
          # Call function with given args
          self.function(*self.args)

     # Function to start repeated timer
     def start(self):
          # Check if the timer is not already running
          if not self.is_running:
               # Set next call to the given interval
               self.next_call += self.interval
               # Create the timer on a new thread
               self._timer = threading.Timer(self.next_call - time.time(), self._run)
               # Start the timer and set running to true
               self._timer.start()
               self.is_running = True

     # Function to stop repeated timer
     def stop(self):
          # Cancel timer thread
          self._timer.cancel()
          # Set running to false
          self.is_running = False


# Establish Tkinter frame as root, set geometry, and resizable off
root = Tk()
root.title("Simple Stock Signal System")
root.geometry("650x700")
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

# Create global variable clickervar to prevent load config from detecting duplicates 
# as it may occur while values are being updated
global clickerVar
clickerVar = False

# Main function to be called when an interval is reached
# Args
# tf = The timeframe interval that is being called
def getData(tf):
     # Get the correct timeframe argument according to the current interval
     apiArgTf = timeFrameDict[tf]
     # Create a list of the symbols to get in this timeframe
     symbolsToGet = []
     # Loop through the combination dictionary, and find which symbols have the
     # same timeframe combination as this interval
     for key in srtCombo:
          if srtCombo[key][5] == tf:
               # If it is the same, append it to the list of symbols to retrieve
               symbolsToGet.append(indDict[srtCombo[key][4]])
     print(symbolsToGet)
     # Create a table for each of the assets
     for assetName in symbolsToGet:
          createTable(assetName, apiArgTf)
     # Set signalCounter to check if signals have been posted
     signalCounter = 0
     # Loop through each symbol
     for asset in symbolsToGet:
          try:
               # Try and retrieve, calculate and insert the data into the database
               calculateAndInsert(asset, apiArgTf)
               # Retrieve data from the databse
               returnedDf = retrieveDataOneTf(symbolsToGet, apiArgTf)
               # Display any signals for the combination to the displayBox
               signalsPrinted = displayChart(returnedDf, displayBox)
               # Increment if a signal was posted
               if signalsPrinted: signalCounter += 1
          # Catch any exceptions and print for debugging
          except Exception as e:
               print(f'There has been an error: {e}')
     # If at least 1 signal has been posted at the end, play an alert to the user
     if signalCounter > 0:  playsound('alert.mp3')
          
# Define callback function for stocks
# Args
# clicker = The StringVar associated with the stock dropdown box
# timeframe = The StringVar associated with the timeframe dropdown box
# clickername = The name identifying the dropdown box being changed
def callback1(clicker, timeframe, clickerName, *args):
     # Check if additional args (clickerVar) is False (process change like normal)
     if not args[0]:
          # Loop through the lists in the dictionary
          for keyName in srtCombo:
               # Check if there is a duplicate combination
               if [clicker.get(), timeframe.get()] == [srtCombo[keyName][4], srtCombo[keyName][5]]:
                    # If the name of the variable is the same as the associated dropdown
                    if clickerName == keyName:
                         # Continue the loop, as this is comparing the traced box with itself
                         continue
                    else:
                         # Else show error to user
                         print(f'A duplicate has been found!')
                         messagebox.showinfo("ERROR", "You cannot have duplicate STOCK/TIMEFRAME combinations!")
                         # Check if there is a stock in the empty space (a new stock)
                         if srtCombo[clickerName][1] == '':
                              # Set the dropdown value to the older selection
                              clicker.set(srtCombo[clickerName][0])
                         else:
                              # Otherwise set it to the newer selection
                              clicker.set(srtCombo[clickerName][1])
                         break
          else:
               # If combo does not exist, allow change and move stock name rotations
               # Check if there is already a stock in the new stock slot
               if srtCombo[clickerName][1] == '':
                    # Set the new stock in the new stock position and current combo position
                    srtCombo[clickerName][1] = clicker.get()
                    srtCombo[clickerName][4] = clicker.get()
               else:
                    # Pop the old stock out and replace with the last stock
                    # Move new stock into new stock and current stock positions
                    srtCombo[clickerName][0] = srtCombo[clickerName][1]
                    srtCombo[clickerName][1] = clicker.get()
                    srtCombo[clickerName][4] = clicker.get()
               print(f'drop variable has been changed to {clicker.get()}')
               print(f'New combo registered as {srtCombo[clickerName][4]}, {srtCombo[clickerName][5]}')
     # Else clickerVar is true (config is being loaded in)
     else:
          # Ignore duplicates and change the values in the same way as above
          if srtCombo[clickerName][1] == '':
               srtCombo[clickerName][1] = clicker.get()
               srtCombo[clickerName][4] = clicker.get()
          else:
               srtCombo[clickerName][0] = srtCombo[clickerName][1]
               srtCombo[clickerName][1] = clicker.get()
               srtCombo[clickerName][4] = clicker.get()
          print(f'drop variable has been changed to {clicker.get()}')
          print(f'New combo registered as {srtCombo[clickerName][4]}, {srtCombo[clickerName][5]}')

# Define callback function for timeframes
# Args
# clicker = The StringVar associated with the stock dropdown box
# timeframe = The StringVar associated with the timeframe drop down box
# clickername = The name identifying the dropdown box being changed
def callback2(clicker, timeframe, clickerName, *args):
     # Check if additional args (clickerVar) is False (process change like normal)
     if not args[0]:
          # Loop through the lists in the dictionary
          for keyName in srtCombo:
               # Check if there is a duplicate combination
               if [clicker.get(), timeframe.get()] == [srtCombo[keyName][4], srtCombo[keyName][5]]:
                    # If the name of the variable is the same as the associated dropdown
                    if clickerName == keyName:
                         # Continue the loop, as this is comparing the traced box with itself
                         continue
                    else:
                         # Else show error to user
                         print(f'A duplicate time has been found!')
                         messagebox.showinfo("ERROR", "You cannot have duplicate STOCK/TIMEFRAME combinations!")
                         # Check if there is a timeframe in the empty space (a new timeframe)
                         if srtCombo[clickerName][3] == '':
                              # Set the dropdown value to the older selection
                              timeframe.set(srtCombo[clickerName][2])
                         else:
                              # Otherwise set it to the newer selection
                              timeframe.set(srtCombo[clickerName][3])
                         break
          else:
               # If combo does not exist, allow change and move timeframe rotations
               # Check if there is already a timeframe in the new timeframe slot
               if srtCombo[clickerName][3] == '':
                    # Set the new timeframe in the new timeframe position and current combo position
                    srtCombo[clickerName][3] = timeframe.get()
                    srtCombo[clickerName][5] = timeframe.get()
               else:
                    # Pop the old timeframe out and replace with the last timeframe
                    # Move new timeframe into new timeframe and current timeframe positions
                    srtCombo[clickerName][2] = srtCombo[clickerName][3]
                    srtCombo[clickerName][3] = timeframe.get()
                    srtCombo[clickerName][5] = timeframe.get()
                    
               print(f'drop variable has been changed to {timeframe.get()}')
               print([clicker.get(), timeframe.get()])

     # Else clickerVar is true (config is being loaded in)
     else:
          # Ignore duplicates and change the values in the same way as above
          if srtCombo[clickerName][3] == '':
               srtCombo[clickerName][3] = timeframe.get()
               srtCombo[clickerName][5] = timeframe.get()
          else:
               srtCombo[clickerName][2] = srtCombo[clickerName][3]
               srtCombo[clickerName][3] = timeframe.get()
               srtCombo[clickerName][5] = timeframe.get()
               
          print(f'drop variable has been changed to {timeframe.get()}')
          print([clicker.get(), timeframe.get()])

# Function to save current stock/time selections to the config file
def saveConfig():
     # Replace each value in the config with the dropdown box value
     stockTfInfo["stock1"] = clicked1.get()
     stockTfInfo["time1"] = timeFrame1.get()

     stockTfInfo["stock2"] = clicked2.get()
     stockTfInfo["time2"] = timeFrame2.get()

     stockTfInfo["stock3"] = clicked3.get()
     stockTfInfo["time3"] = timeFrame3.get()

     stockTfInfo["stock4"] = clicked4.get()
     stockTfInfo["time4"] = timeFrame4.get()

     stockTfInfo["stock5"] = clicked5.get()
     stockTfInfo["time5"] = timeFrame5.get()

     # Open the config file in write mode
     with open('config.ini', 'w') as conf:
          # Write to the config to save changes
          config_object.write(conf)
     # Close the config file
     conf.close()
     print("Config written to!")

# Function to load config file
def loadConfig():
     # Make local clickerVar variable global and set it to true to bypass trace function checks
     global clickerVar
     clickerVar = True
     # Set the dropdown boxes values according to the values in the config
     clicked1.set(stockTfInfo["stock1"])
     timeFrame1.set(stockTfInfo["time1"])

     clicked2.set(stockTfInfo["stock2"])
     timeFrame2.set(stockTfInfo["time2"])

     clicked3.set(stockTfInfo["stock3"])
     timeFrame3.set(stockTfInfo["time3"])

     clicked4.set(stockTfInfo["stock4"])
     timeFrame4.set(stockTfInfo["time4"])

     clicked5.set(stockTfInfo["stock5"])
     timeFrame5.set(stockTfInfo["time5"])
     print("Config loaded!")
     # Set clickerVar back to false so any further changes are checked as normal
     clickerVar = False

# Stock 1/Timeframe 1
# #####################################
# Initialize srtCombo
srtCombo["clicked1"][0] = clicked1.get()
srtCombo["clicked1"][2] = timeFrame1.get()
srtCombo["clicked1"][4] = clicked1.get()
srtCombo["clicked1"][5] = timeFrame1.get()
# Add trace functions to dropdown boxes, using lambda and placeholder variables to pass variables to trace function
clicked1.trace_add("write", lambda var_name, var_index, operation: callback1(clicked1, timeFrame1, "clicked1", clickerVar))
timeFrame1.trace_add("write", lambda var_name, var_index, operation: callback2(clicked1, timeFrame1, "clicked1", clickerVar))
#####################################

# Stock 2/Timeframe 2
#####################################
srtCombo["clicked2"][0] = clicked2.get()
srtCombo["clicked2"][2] = timeFrame2.get()
srtCombo["clicked2"][4] = clicked2.get()
srtCombo["clicked2"][5] = timeFrame2.get()
clicked2.trace_add("write", lambda var_name, var_index, operation: callback1(clicked2, timeFrame2, "clicked2", clickerVar))
timeFrame2.trace_add("write", lambda var_name, var_index, operation: callback2(clicked2, timeFrame2, "clicked2", clickerVar))
#####################################

# Stock 3/Timeframe 3
#####################################
srtCombo["clicked3"][0] = clicked3.get()
srtCombo["clicked3"][2] = timeFrame3.get()
srtCombo["clicked3"][4] = clicked3.get()
srtCombo["clicked3"][5] = timeFrame3.get()
clicked3.trace_add("write", lambda var_name, var_index, operation: callback1(clicked3, timeFrame3, "clicked3", clickerVar))
timeFrame3.trace_add("write", lambda var_name, var_index, operation: callback2(clicked3, timeFrame3, "clicked3", clickerVar))
#####################################

# Stock 4/Timeframe 4
#####################################
srtCombo["clicked4"][0] = clicked4.get()
srtCombo["clicked4"][2] = timeFrame4.get()
srtCombo["clicked4"][4] = clicked4.get()
srtCombo["clicked4"][5] = timeFrame4.get()
clicked4.trace_add("write", lambda var_name, var_index, operation: callback1(clicked4, timeFrame4, "clicked4", clickerVar))
timeFrame4.trace_add("write", lambda var_name, var_index, operation: callback2(clicked4, timeFrame4, "clicked4", clickerVar))
#####################################

# Stock 5/Timeframe 5
#####################################
srtCombo["clicked5"][0] = clicked5.get()
srtCombo["clicked5"][2] = timeFrame5.get()
srtCombo["clicked5"][4] = clicked5.get()
srtCombo["clicked5"][5] = timeFrame5.get()
clicked5.trace_add("write", lambda var_name, var_index, operation : callback1(clicked5, timeFrame5, "clicked5", clickerVar))
timeFrame5.trace_add("write", lambda var_name, var_index, operation: callback2(clicked5, timeFrame5, "clicked5", clickerVar))
#####################################

# Create dropdown box as OptionMenu, passing tkinter root, dropdown box stringvar and list of stock names. Configure size, colour and positioning
drop1 = OptionMenu(root, clicked1, *stockNameList)
drop1.config(width=25, bg="green", foreground="white")
drop1.place(x=0, y=0)

# Create get chart button, size and positioning, and setting command to function to display chart with signals, passing stock and timeframe as args
button1 = Button(root, text="Get chart")
button1.columnconfigure(0, weight=0)
button1.place(x=0, y=35)
button1['command'] = lambda:displayChartWithSignals(clicked1.get(), timeFrame1.get()) 

# Create timeframe dropdown as OptionMenu, passing tkinter root, dropdown box stringvar, and list of timeframes. Configure size, colour and positioning
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

# Load config after creation of the dropdown boxes
loadConfig()

########################################################

# Create button to load config, giving loadConfig function as command. Configure size, colour and positioning
loadConfig = Button(root, text="Load Selections", command=loadConfig)
loadConfig.config(width=15, bg="white", foreground="black")
loadConfig.place(x=320, y=600)

# Create button to save config, giving saveConfig function as command. Configure size, colour and positioning
saveConfig = Button(root, text="Save Selections", command=saveConfig)
saveConfig.config(width=15, bg="white", foreground="black")
saveConfig.place(x=440, y=600)

# Create button to exit application, giving destroy function as command to kill GUI, ending the program execution. Configure size, colour and positioning
exitButton = Button(root, text="Exit", command=root.destroy)
exitButton.config(width=10, bg="red", foreground="white")
exitButton.place(x=560, y=600)

########################################################

# Create displaybox to display signals. Configure size, colour and positioning
displayBox = st.ScrolledText(root, width=29, height=23, font=("Calibri", 15))
displayBox.place(x=335, y=2)
# Add tags to displayBox to change colour of text when BUY or SELL is in the text
displayBox.tag_configure('BUY', background='black', foreground='lime')
displayBox.tag_configure('SELL', background='black', foreground='red')
# Disable box so that user can't edit it
displayBox.configure(state="disabled")

########################################################

# Create label and text box for displaying top 5 performing stocks
top5Label = Label(root, text="Top 5 Performers (Percent increase from yesterday)", foreground="green").place(x=10, y=400)
top5Box = Text(root, width=45, height=8, font=("Calibri", 10))
top5Box.place(x=10, y=420)
# Disable box so that user can't edit it
top5Box.configure(state="disabled")

########################################################

# Create label and text box for displaying worst 5 performing stocks
bot5Label = Label(root, text="Worst 5 Performers (Percent decrease from yesterday)", foreground="red").place(x=10, y=546)
bot5Box = Text(root, width=45, height=8, font=("Calibri", 10))
bot5Box.place(x=10, y=570)
# Disable box so that user can't edit it
bot5Box.configure(state="disabled")

########################################################

# Set up initial number of seconds to wait from now until the next interval
fiveMinSyncTime = syncTiming5()
thirtyMinSyncTime = syncTiming30()
hourSyncTime = syncTiming60()

# Print to console for debugging
print(f'Five mins in: {fiveMinSyncTime} seconds')
print(f'Thirty mins in: {thirtyMinSyncTime} seconds')
print(f'One hour in: {hourSyncTime} seconds')

# Create repeated timer opbjects with timing until next interval, getData function to be activated on interval, and timeframe string to identify which timeframe
_5minThread = RepeatedTimer(fiveMinSyncTime, getData, "5MIN")
_30minThread = RepeatedTimer(thirtyMinSyncTime, getData, "30MIN")
_1hThread = RepeatedTimer(hourSyncTime, getData, "1HOUR")

# Set the interval after first run to respective time in seconds + 1
_5minThread.interval = 301
_30minThread.interval = 1801
_1hThread.interval = 3601

# Set icon
root.iconbitmap('ticker.ico')
# Display top and worst performing stocks to the displayboxes
getRecentDayPctDiff(top5Box, bot5Box)
# Start main event loop
root.mainloop()

# Stop timer threads after GUI exection ends
# Otherwise threads will cause program to continue to run
_5minThread.stop()
_30minThread.stop()
_1hThread.stop()