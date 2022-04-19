from logging import root
import tkinter as tk

class Window:
    def __init__(self, master):
        self.master = root

        self.frame = tk.Frame(self.master, width = 750, height=720)
        self.frame.pack()

        self.mbutton = tk.Menubutton(self.frame, text="Stonks", relief=tk.RAISED)

        self.menu = tk.Menu(self.mbutton, tearoff=0)
        self.var1 = tk.IntVar()
        self.var2 = tk.IntVar()
        self.menu.add_checkbutton(label="Option 1", variable=self.var1, command=self.command1)
        self.menu.add_checkbutton(label="Option 1", variable=self.var2, command=self.command1)
        self.mbutton['menu'] = self.menu

        self.mbutton.place(x=50, y=50)


    def command1(self):
        print(self.var1.get())
        print(self.var2.get())


root = tk.Tk()
window = Window(root)
root.mainloop()