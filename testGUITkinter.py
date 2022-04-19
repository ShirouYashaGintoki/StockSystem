from tkinter import *

from matplotlib.pyplot import get

listOfIndices = ["AMZN", "PLOP", "TURD"]


root = Tk()
root.title("Simple Stock Signal System")
root.geometry("750x720")
root.resizable(False, False)

clicked1 = StringVar(root)
clicked1.set(listOfIndices[0])

clicked2 = StringVar(root)
clicked2.set(listOfIndices[0])

clicked3 = StringVar(root)
clicked3.set(listOfIndices[0])

clicked4 = StringVar(root)
clicked4.set(listOfIndices[0])

clicked5 = StringVar(root)
clicked5.set(listOfIndices[0])


def beans():
    print("Beans alert")

mB = Menubutton(root, text="Test menu button")

testMenu = Menu(mB, tearoff=0)
testMenu.add_command(label="poo", command=beans)
mB['menu'] = Menu

mB.place(x=50, y=50)

# drop1 = OptionMenu(root, clicked1, *listOfIndices)
# drop1.config(width=20, bg="green", foreground="white")
# drop1.grid(row=0, column=0)

# button1 = Button(root, text="Get chart")
# button1.columnconfigure(0, weight=0)
# button1.grid(row=1, column=0, sticky=W)

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