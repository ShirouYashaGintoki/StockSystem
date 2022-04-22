from tkinter import *
import pandas as pd
from varname import nameof, argname, varname

# Indices as dataframe, Sheet 1 is main sheet, Sheet 2 has 5 for testing
indices = pd.read_excel('tickers2.xlsx', sheet_name='Sheet 1')

# Tickers is a list of symbols as strings from the 'Symbol' column
# of the dataframe 'indices'
tickers = sorted(indices['Symbol'])
# List of timeframes, to be changed to 5min, 30min, 1h
timeFrames = ['HOURLY', 'DAILY', 'WEEKLY']

# Create list to handle previous selection of stock

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

# stockRotations = [
#      ['', ''],
#      ['', ''],
#      ['', ''],
#      ['', ''],
#      ['', '']
# ]

# timeRotations = [
#      ['', ''],
#      ['', ''],
#      ['', ''],
#      ['', ''],
#      ['', '']
# ]

# stockTimeCombo = [
#      ['', ''],
#      ['', ''],
#      ['', ''],
#      ['', ''],
#      ['', '']
# ]

root = Tk()
root.title("Simple Stock Signal System")
root.geometry("750x720")
root.resizable(False, False)

clicked1   = StringVar(root, name="beans")
clicked2   = StringVar(root)
clicked3   = StringVar(root)
clicked4   = StringVar(root)
clicked5   = StringVar(root)
timeFrame1 = StringVar(root)
timeFrame2 = StringVar(root)

def callback1(clicker, timeframe, clickerName):
     # When dropdown is changed, check if its combo exists
     print(clicker.get(), timeframe.get())
     # clickerName = argname(clicker)
     for keyName in srtCombo:
          print(srtCombo[keyName])
          print(clickerName, keyName)
          print(f'{clicker.get()}, {timeframe.get()} vs {srtCombo[keyName][4]}, {srtCombo[keyName][5]}')
          if [clicker.get(), timeframe.get()] == [srtCombo[keyName][4], srtCombo[keyName][5]]:
               print(f'A duplicate has been found!')
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
          else:
               srtCombo[clickerName][0] = srtCombo[clickerName][1]
               srtCombo[clickerName][1] = clicker.get()
          print(f'drop variable has been changed to {clicker.get()}')
          print([clicker.get(), timeframe.get()])
          

# Stock 1
#####################################
clicked1.set(tickers[0])
timeFrame1.set(timeFrames[0])
srtCombo["clicked1"][0] = clicked1.get()
srtCombo["clicked1"][2] = timeFrame1.get()
srtCombo["clicked1"][4] = clicked1.get()
srtCombo["clicked1"][5] = timeFrame1.get()
clicked1.trace_add("write", lambda var_name, var_index, operation: callback1(clicked1, timeFrame1, "clicked1"))

#####################################

# Stock 2
#####################################
clicked2.set(tickers[1])
timeFrame2.set(timeFrames[0])
srtCombo["clicked2"][0] = clicked2.get()
srtCombo["clicked2"][2] = timeFrame2.get()
srtCombo["clicked2"][4] = clicked2.get()
srtCombo["clicked2"][5] = timeFrame2.get()
# clicked2.trace("w", callback1)
#####################################

clicked3.set(tickers[2])
clicked4.set(tickers[3])
clicked5.set(tickers[4])

drop1 = OptionMenu(root, clicked1, *tickers)
drop1.config(width=22, bg="green", foreground="white")
drop1.place(x=0, y=0)

button1 = Button(root, text="Get chart")
button1.columnconfigure(0, weight=0)
button1.place(x=0, y=35)

dropTf1 = OptionMenu(root, timeFrame1, *timeFrames)
dropTf1.config(width=10, bg="blue", foreground="white")
dropTf1.place(x=72, y=32)

drop2 = OptionMenu(root, clicked2, *tickers)
drop2.config(width=20, bg="green", foreground="white")
drop2.place(x=0, y=80)

button2 = Button(root, text="Get chart")
button2.columnconfigure(0, weight=0)
button2.place(x=0, y=115)

dropTf2 = OptionMenu(root, timeFrame2, *timeFrames)
dropTf2.config(width=10, bg="blue", foreground="white")
dropTf2.place(x=72, y=112)

# drop3 = OptionMenu(root, clicked3, *listOfIndices)
# drop3.config(width=20, bg="green", foreground="white")
# drop3.grid(row=4, column=0)
# button3 = Button(root, text="Get chart")
# button3.columnconfigure(0, weight=0)
# button3.grid(row=5, column=0, sticky=W)

# drop4 = OptionMenu(root, clicked4, *listOfIndices)
# drop4.config(width=20, bg="green", foreground="white")
# drop4.grid(row=6, column=0)
# button4 = Button(root, text="Get chart")
# button4.columnconfigure(0, weight=0)
# button4.grid(row=7, column=0, sticky=W)

# drop5 = OptionMenu(root, clicked5, *listOfIndices)
# drop5.config(width=20, bg="green", foreground="white")
# drop5.grid(row=8, column=0)
# button5 = Button(root, text="Get chart")
# button5.columnconfigure(0, weight=0)
# button5.grid(row=9, column=0, sticky=W)



# exitButton = Button(root, text="Exit", command=root.destroy)
# exitButton.config(width=10, bg="red", foreground="white")
# exitButton.columnconfigure(0, weight=0)
# exitButton.grid(row=10, column=10, sticky=S+E)
# drop.pack()


mainloop()