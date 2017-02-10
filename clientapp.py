import time
import socket
import hashlib
import threading as thr

from tkinter import *
from tkinter import messagebox as tkmb

HIM = "127.0.0.1"
MAXLINE = 200

class Main(Tk):

    def __init__(self):
        super(Main, self).__init__()

        # self.geometry("400x400")
        self.protocol("WM_DELETE_WINDOW", self.teardown)
        self.title("Titokminiszter")

        self.running = True
        self.connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connector = thr.Thread(target=self.connect)
        self.listener = thr.Thread(target=self.listen)

        self.label = Label(self, text="Inicializálás...")
        self.label.pack(fill=BOTH)
        fr = Frame(self)
        fr.pack()
        self.lb = Listbox(fr, width=80, height=20, state=DISABLED)
        self.lb.pack(side=RIGHT)
        sb = Scrollbar(fr)
        sb.pack(side=RIGHT)
        self.lb.config(yscrollcommand=sb.set)
        sb.config(command=self.lb.yview)

        self.entry = Entry(self, show="*")
        self.entry.bind("<Return>", self.authenticate)
        self.entry.pack(fill=BOTH)
        Button(self, text="Kilép", command=self.teardown).pack(fill=BOTH)

    def inject_line(self, line):
        lbs = self.lb.size()
        if lbs >= MAXLINE:
            self.lb.delete(0)
            for i in range(1, lbs):
                self.lb.insert(i-1, self.lb.get(i))
        self.lb.insert(END, line)
        self.lb.see(END)

    def connect(self):
        self.label.configure(text="Várakozás kapcsolatra...")
        while 1:
            try:
                self.socket.connect((HIM, 12345))
            except ConnectionRefusedError:
                time.sleep(1)
                print("Awaiting connection...")
            else:
                self.label.configure(text="Kapcsolat felépítve")
                break

        self.lb.insert(END, "Kérem szépen a jelszót!")

        msg = b""
        while msg[-5:] != b"ROGER":
            msg += self.socket.recv(1024)
            time.sleep(0.1)
        if msg[:-5] == b"SODOFF":
            tkmb.showerror("Autentikációs hiba!", "Helytelen jelszó! Leállás...")
            self.teardown()
        else:
            self.label.configure(text="Autentikálva")

        self.connected = True
        self.listener.start()

    def authenticate(self, event=None):
        del event
        hasher = hashlib.sha1()
        pw = self.entry.get()
        print("pw:", pw)
        if not pw:
            return
        hasher.update(pw.encode())
        self.socket.sendall(hasher.digest() + b"ROGER")

        self.entry.delete(0, END)
        self.entry.configure(show="")
        self.entry.unbind("<Return>")
        self.entry.bind("<Return>", self.send_message)

    def listen(self):
        print("Listener starting...")
        while not self.connected:
            time.sleep(1)
            print("Client listener: Awaiting connection...")
        while self.running:
            msg = b""
            while msg[-5:] != b"ROGER":
                msg += self.socket.recv(1024)
                time.sleep(0.1)
            self.inject_line("Ő: " + msg[:-5].decode("utf8"))
        print("Listener exiting...")

    def send_message(self, event=None):
        del event
        try:
            msg = self.entry.get()
            self.socket.sendall(msg.encode() + b"ROGER")
        except BrokenPipeError:
            tkmb.showerror("Hiba!", "A másik fél kilépett! Kilépés...")
            self.teardown()
        else:
            self.inject_line("ÉN: " + msg)
            self.entry.delete(0, END)
            self.entry.focus_set()

    def teardown(self):
        self.running = False
        self.label.config(text="Kilépés...")
        time.sleep(1)
        self.socket.close()
        self.destroy()

if __name__ == '__main__':
    app = Main()
    app.connector.start()
    app.mainloop()
