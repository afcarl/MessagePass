from tkinter import *


class Main(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.lb = Listbox(self, height=5)
        self.lb.pack()

        for i in range(4):
            print(i)
            self.lb.insert(0, "HI")
        self.lb.insert(END, "1")

        Button(self, text="Jolly", command=self.jolly).pack()

    def jolly(self):
        items = [self.lb.get(i) for i in range(self.lb.size())]
        self.lb.delete(0, END)
        for item in items[1:]:
            self.lb.insert(END, item)
        self.lb.insert(END, 2)

if __name__ == '__main__':
    app = Main()
    app.mainloop()
