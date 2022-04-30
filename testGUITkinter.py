from re import L
from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext as st
import pandas as pd
from pandas import json_normalize
import threading
import time
from datetime import datetime
import requests
import tabulate


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

# Tickers is a list of symbols as strings from the 'Symbol' column
# of the dataframe 'indices'
# tickers = sorted(indices['Symbol'])

# List of timeframes, to be changed to 5min, 30min, 1h
# 1h has a time signal of HH:30
# 30min is anything either HH:00 or HH:30
# 5min has anything that is a multiple of 5
timeFrames = ['5MIN', '30MIN', '1HOUR']

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
     now = str(datetime.now())
     # Split string by colon
     splitNow = now.split(":")
     # Get minutes and seconds as ints from split list by typecasting
     minutes = int(splitNow[1])
     seconds = int(float(splitNow[2]))
     # Check if minutes is already a multiple of 5
     if minutes % 5 == 0:
          # Check if the minute is close to completion
          if seconds > 30:
               # If so, add an extra minute
               return 6
          else:
               # Otherwise return 5
               return 5
     else:
          # Else need to find the next multiple of 5
          # Set counter
          counter = 0
          min2 = minutes
          # Loop until min2 is a multiple of 5
          while min2 % 5 != 0:
               min2 += 1
               counter += 1
          if seconds > 30:
               counter += 1
          return counter 

def syncTiming30():
     now = str(datetime.now())
     splitNow = now.split(":")
     minutes = int(splitNow[1])
     seconds = int(float(splitNow[2]))
     if minutes == 30 or minutes == 0:
          if seconds > 30:
               return 31
          else:
               return 30
     else:
          if minutes > 30:
               ttw = 60 - minutes
               if seconds > 30:
                    ttw += 1
               return ttw
          else:
               ttw = 30 - minutes
               if seconds > 30:
                    ttw += 1
               return ttw

def syncTiming60():
     now = str(datetime.now())
     splitNow = now.split(":")
     minutes = int(splitNow[1])
     seconds = int(float(splitNow[2]))
     if minutes == 30 or minutes == 0:
          if minutes == 30:
               if seconds > 30:
                    return 61
               else:
                    return 60
          elif minutes == 0:
               if seconds > 30:
                    return 31
               else:
                    return 30
     else:
          if minutes > 30:
               ttw = (60 - minutes) + 60
               return ttw
          else:
               ttw = 30 - minutes
               return ttw


def getData(tf):
     if tf == "5MIN" :
          print("5MIN interval reached")
          symbolsToGet = []
          for key in srtCombo:
               if srtCombo[key][5] == "5MIN":
                    symbolsToGet.append(indDict[srtCombo[key][4]])
          print(symbolsToGet)
          for asset in symbolsToGet:
               try:
                    querystring = {"symbol":asset,"interval":"1h","outputsize":"30","format":"json"}
                    response = requests.request("GET", url, headers=headers, params=querystring)
                    jsonResponse = response.json()
                    df2 = json_normalize(jsonResponse, 'values')
                    # print(tabulate(df2, showindex=False, headers=list(df2.columns)))
               except Exception as e:
                    print(f'There has been an error: {e}')
     if tf == "30MIN":
          print("30MIN interval reached")
     if tf == "1HOUR":
          print("1HOUR interval reached")
     print(datetime.now())
     
          
# Define callback function
# Args
# clicker = The StringVar associated with the stock dropdown box
# timeframe = The StringVar associated with the timeframe dropdown box
# clickername = The name identifying the dropdown box being changed
def callback1(clicker, timeframe, clickerName):
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
clicked5.trace_add("write", lambda var_name, var_index, operation: callback1(clicked5, timeFrame5, "clicked5"))
timeFrame5.trace_add("write", lambda var_name, var_index, operation: callback2(clicked5, timeFrame5, "clicked5"))
#####################################
stockNameList
drop1 = OptionMenu(root, clicked1, *stockNameList)
drop1.config(width=25, bg="green", foreground="white")
drop1.place(x=0, y=0)

button1 = Button(root, text="Get chart")
button1.columnconfigure(0, weight=0)
button1.place(x=0, y=35)

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

dropTf2 = OptionMenu(root, timeFrame2, *timeFrames)
dropTf2.config(width=10, bg="blue", foreground="white")
dropTf2.place(x=90, y=112)

########################################################

drop3 = OptionMenu(root, clicked3, *stockNameList)
drop3.config(width=25, bg="green", foreground="white")
drop3.place(x=0, y=160)

button3 = Button(root, text="Get chart")
button3.columnconfigure(0, weight=0)
button3.place(x=0, y=195)

dropTf3 = OptionMenu(root, timeFrame3, *timeFrames)
dropTf3.config(width=10, bg="blue", foreground="white")
dropTf3.place(x=90, y=192)

########################################################

drop4 = OptionMenu(root, clicked4, *stockNameList)
drop4.config(width=25, bg="green", foreground="white")
drop4.place(x=0, y=240)

button4 = Button(root, text="Get chart")
button4.columnconfigure(0, weight=0)
button4.place(x=0, y=275)

dropTf4 = OptionMenu(root, timeFrame4, *timeFrames)
dropTf4.config(width=10, bg="blue", foreground="white")
dropTf4.place(x=90, y=272)

# ########################################################

drop5 = OptionMenu(root, clicked5, *stockNameList)
drop5.config(width=25, bg="green", foreground="white")
drop5.place(x=0, y=320)

button5 = Button(root, text="Get chart")
button5.columnconfigure(0, weight=0)
button5.place(x=0, y=355)

dropTf5 = OptionMenu(root, timeFrame5, *timeFrames)
dropTf5.config(width=10, bg="blue", foreground="white")
dropTf5.place(x=90, y=352)

########################################################

exitButton = Button(root, text="Exit", command=root.destroy)
exitButton.config(width=10, bg="red", foreground="white")
exitButton.place(x=560, y=570)

########################################################

displayBox = st.ScrolledText(root, width=25, height=25, font=("Times New Roman", 15))
displayBox.place(x=300, y=2)
# displayBox.tag_config('BUY', background="black", foreground="lime")
# displayBox.insert('end', "Hello\n", 'BUY')
# displayBox.insert(tkinter.INSERT, "BUY SIGNAL\n")
# displayBox.insert(tkinter.INSERT, "BEAN SIGNAL\n")
# displayBox.delete("1.0","end")
displayBox.configure(state="disabled")

# def hello(name):
#      print(f'hello {name}')

# rt = RepeatedTimer(1, hello, "beans") 

fiveMinSyncTime = syncTiming5() * 60
thirtyMinSyncTime = syncTiming30() *60
hourSyncTime = syncTiming60() * 60

print(f'Five mins in: {fiveMinSyncTime} seconds')
print(f'Thirty mins in: {thirtyMinSyncTime} seconds ')
print(f'One hour in: {hourSyncTime} seconds')

_5minThread = RepeatedTimer(fiveMinSyncTime, getData, "5MIN")
_30minThread = RepeatedTimer(thirtyMinSyncTime, getData, "30MIN")
_1hThread = RepeatedTimer(hourSyncTime, getData, "1HOUR")

_5minThread.interval = 300
_30minThread.interval = 1800
_1hThread.interval = 3600

root.mainloop()

_5minThread.stop()
_30minThread.stop()
_1hThread.stop()