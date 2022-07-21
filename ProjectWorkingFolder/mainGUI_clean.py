from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext as st
import pandas as pd
import threading
import time
import mysql.connector
import traceback
from configparser import ConfigParser
from configSetup import ftConfigSetup
from timing import syncTiming5, syncTiming30, syncTiming60

try:
     with open("config.ini") as cfg:
          print("Config found!")
          cfg.close()
except Exception as e:
     print(e)
     print("Config not found")
     ftConfigSetup()
     print("Config created!")

from displayDataFunctions import displayChartWithSignals, displayChart, getRecentDayPctDiff
from dbFunctions import retrieveDataOneTf, createTable, calculateAndInsert


config_object = ConfigParser()
config_object.read("config.ini")
dbInfo = config_object["DATABASE"]
apiInfo = config_object["API"]
stockTfInfo = config_object["STOCKCONFIG"]

# Indices as dataframe
indices = pd.read_excel('tickers.xlsx', sheet_name='Sheet 1')
# Create a dictionary of stock names and their ticker symbols
indDict = pd.Series(indices.Symbol.values, index=indices.CompanyName).to_dict()
# print(indDict)
# Create a list of stock names for display purposes
stockNameList = sorted(list(indDict.keys()))

# List of timeframes, to be changed to 5min, 30min, 1h
# 1h has a time signal of HH:30
# 30min is anything either HH:00 or HH:30
# 5min has anything that is a multiple of 5
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

# beansontoastA1? for PC
# Establish connection using mysql connector
try:
     db = mysql.connector.connect(
     host=dbInfo['host'],
     user=dbInfo['user'],
     passwd=dbInfo['password']
     )
except Exception as e:
     print(e)
     messagebox.showinfo("ERROR", "You cannot have duplicate STOCK/TIMEFRAME combinations!")
     exit()

# Create cursor
my_cursor = db.cursor()

# Try to create database, catch exception if fails
try:
     my_cursor.execute("CREATE DATABASE StockTables")
except Exception:
     print("DB schema already exists")

# Close database connection now
db.close()

# Function found on stackoverflow by eraoul
# https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds
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

global clickerVar
clickerVar = False

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
               print("RETURNED DF CHECK SELECTOR")
               print(returnedDf)
               displayChart(returnedDf, displayBox)
          except Exception as e:
               print(f'There has been an error: {e}')
               print(traceback.format_exc())
          
# Define callback function
# Args
# clicker = The StringVar associated with the stock dropdown box
# timeframe = The StringVar associated with the timeframe drop down box
# clickername = The name identifying the dropdown box being changed
def callback1(clicker, timeframe, clickerName, *args):
     # When dropdown is changed, check if its combo exists
     if not args[0]:
          for keyName in srtCombo:
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


def callback2(clicker, timeframe, clickerName, *args):
     # When dropdown is changed, check if its combo exists
     if not args[0]:
          for keyName in srtCombo:
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
     global clickerVar
     clickerVar = True
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
     clickerVar = False

# def test():
#      top5Box.configure(state="normal")
#      top5Box.insert("end", "plop")
#      top5Box.configure(state="disabled")

# Stock 1
#####################################
clicked1.set(stockNameList[0])
timeFrame1.set(timeFrames[0])
srtCombo["clicked1"][0] = clicked1.get()
srtCombo["clicked1"][2] = timeFrame1.get()
srtCombo["clicked1"][4] = clicked1.get()
srtCombo["clicked1"][5] = timeFrame1.get()
clicked1.trace_add("write", lambda var_name, var_index, operation: callback1(clicked1, timeFrame1, "clicked1", clickerVar))
timeFrame1.trace_add("write", lambda var_name, var_index, operation: callback2(clicked1, timeFrame1, "clicked1", clickerVar))

#####################################

# Stock 2
#####################################
clicked2.set(stockNameList[1])
timeFrame2.set(timeFrames[0])
srtCombo["clicked2"][0] = clicked2.get()
srtCombo["clicked2"][2] = timeFrame2.get()
srtCombo["clicked2"][4] = clicked2.get()
srtCombo["clicked2"][5] = timeFrame2.get()
clicked2.trace_add("write", lambda var_name, var_index, operation: callback1(clicked2, timeFrame2, "clicked2", clickerVar))
timeFrame2.trace_add("write", lambda var_name, var_index, operation: callback2(clicked2, timeFrame2, "clicked2", clickerVar))
#####################################

# Stock 3
#####################################
clicked3.set(stockNameList[2])
timeFrame3.set(timeFrames[0])
srtCombo["clicked3"][0] = clicked3.get()
srtCombo["clicked3"][2] = timeFrame3.get()
srtCombo["clicked3"][4] = clicked3.get()
srtCombo["clicked3"][5] = timeFrame3.get()
clicked3.trace_add("write", lambda var_name, var_index, operation: callback1(clicked3, timeFrame3, "clicked3", clickerVar))
timeFrame3.trace_add("write", lambda var_name, var_index, operation: callback2(clicked3, timeFrame3, "clicked3", clickerVar))
#####################################

# Stock 4
#####################################
clicked4.set(stockNameList[3])
timeFrame4.set(timeFrames[0])
srtCombo["clicked4"][0] = clicked4.get()
srtCombo["clicked4"][2] = timeFrame4.get()
srtCombo["clicked4"][4] = clicked4.get()
srtCombo["clicked4"][5] = timeFrame4.get()
clicked4.trace_add("write", lambda var_name, var_index, operation: callback1(clicked4, timeFrame4, "clicked4", clickerVar))
timeFrame4.trace_add("write", lambda var_name, var_index, operation: callback2(clicked4, timeFrame4, "clicked4", clickerVar))
#####################################

# Stock 5
#####################################
clicked5.set(stockNameList[4])
timeFrame5.set(timeFrames[0])
srtCombo["clicked5"][0] = clicked5.get()
srtCombo["clicked5"][2] = timeFrame5.get()
srtCombo["clicked5"][4] = clicked5.get()
srtCombo["clicked5"][5] = timeFrame5.get()
clicked5.trace_add("write", lambda var_name, var_index, operation : callback1(clicked5, timeFrame5, "clicked5", clickerVar))
timeFrame5.trace_add("write", lambda var_name, var_index, operation: callback2(clicked5, timeFrame5, "clicked5", clickerVar))
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

loadConfig()

########################################################

loadConfig = Button(root, text="Load Selections", command=loadConfig)
loadConfig.config(width=15, bg="white", foreground="black")
loadConfig.place(x=320, y=600)

saveConfig = Button(root, text="Save Selections", command=saveConfig)
saveConfig.config(width=15, bg="white", foreground="black")
saveConfig.place(x=440, y=600)

exitButton = Button(root, text="Exit", command=root.destroy)
exitButton.config(width=10, bg="red", foreground="white")
exitButton.place(x=560, y=600)

########################################################

displayBox = st.ScrolledText(root, width=29, height=23, font=("Calibri", 15))
displayBox.place(x=335, y=2)
displayBox.tag_configure('BUY', background='black', foreground='lime')
displayBox.tag_configure('SELL', background='black', foreground='red')
displayBox.configure(state="disabled")

########################################################

top5Label = Label(root, text="Top 5 Performers (Percent increase from yesterday)", foreground="green").place(x=10, y=400)
top5Box = Text(root, width=45, height=8, font=("Calibri", 10))
top5Box.place(x=10, y=420)
top5Box.configure(state="disabled")

########################################################

bot5Label = Label(root, text="Worst 5 Performers (Percent decrease from yesterday)", foreground="red").place(x=10, y=546)
bot5Box = Text(root, width=45, height=8, font=("Calibri", 10))
bot5Box.place(x=10, y=570)
bot5Box.configure(state="disabled")

########################################################

fiveMinSyncTime = syncTiming5()
thirtyMinSyncTime = syncTiming30()
hourSyncTime = syncTiming60()

print(f'Five mins in: {fiveMinSyncTime} seconds')
print(f'Thirty mins in: {thirtyMinSyncTime} seconds')
print(f'One hour in: {hourSyncTime} seconds')

_5minThread = RepeatedTimer(fiveMinSyncTime, getData, "5MIN")
_30minThread = RepeatedTimer(thirtyMinSyncTime, getData, "30MIN")
_1hThread = RepeatedTimer(hourSyncTime, getData, "1HOUR")

_5minThread.interval = 301
_30minThread.interval = 1801
_1hThread.interval = 3601

root.iconbitmap('ticker.ico')
# Begin Tkinter GUI event loop
getRecentDayPctDiff(top5Box, bot5Box)
root.mainloop()

# Stop timer threads after GUI exection ends
# Otherwise threads will cause program to continue to run
_5minThread.stop()
_30minThread.stop()
_1hThread.stop()