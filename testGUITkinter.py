from tkinter import *
import pandas as pd

# Indices as dataframe, Sheet 1 is main sheet, Sheet 2 has 5 for testing
indices = pd.read_excel('tickers2.xlsx', sheet_name='Sheet 1')

# Tickers is a list of symbols as strings from the 'Symbol' column
# of the dataframe 'indices'
tickers = sorted(indices['Symbol'])

print(tickers)
setTickers = ['', '', '', '', '']

root = Tk()
root.title("Simple Stock Signal System")
root.geometry("750x720")
root.resizable(False, False)

clicked1 = StringVar(root)

def callback(*args):
     if setTickers.count(clicked1.get()) >= 1:
          print(f'The variable {clicked1.get()} already exists')
     
     print(f"the variable has changed to '{clicked1.get()}'")

clicked1.set(tickers[0])
print(setTickers)
clicked1.trace("w", callback)


clicked2 = StringVar(root)
clicked2.set(tickers[0])

clicked3 = StringVar(root)
clicked3.set(tickers[0])

clicked4 = StringVar(root)
clicked4.set(tickers[0])

clicked5 = StringVar(root)
clicked5.set(tickers[0])


drop1 = OptionMenu(root, clicked1, *tickers)
drop1.config(width=20, bg="green", foreground="white")
drop1.grid(row=0, column=0)

button1 = Button(root, text="Get chart")
button1.columnconfigure(0, weight=0)
button1.grid(row=1, column=0, sticky=W)

# drop2 = OptionMenu(root, clicked2, *listOfIndices)
# drop2.config(width=20, bg="green", foreground="white")
# drop2.grid(row=2, column=0)
# button2 = Button(root, text="Get chart")
# button2.columnconfigure(0, weight=0)
# button2.grid(row=3, column=0, sticky=W)

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