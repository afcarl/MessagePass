import time
import socket
import hashlib
import threading as thr

from tkinter import *
from tkinter import messagebox as tkmb

HIM = "127.0.0.1"
MAXLINE = 20


def my_ip():
    return socket.gethostbyname(socket.gethostname())


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
        self.lb = Listbox(fr, width=80, height=MAXLINE)
        self.lb.pack(side=RIGHT)
        # sb = Scrollbar(fr)
        # sb.pack(side=RIGHT)
        # self.lb.config(yscrollcommand=sb.set)
        # sb.config(command=self.lb.yview)

        self.entry = Entry(self, show="*")
        self.entry.bind("<Return>", self.authenticate)
        self.entry.pack(fill=BOTH)
        Button(self, text="Kilép", command=self.teardown).pack(fill=BOTH)

    def inject_line(self, line):
        lbs = self.lb.size()
        if lbs >= MAXLINE:
            items = [self.lb.get(i) for i in range(lbs)]
            self.lb.delete(0, END)
            for item in items[1:]:
                self.lb.insert(END, item)
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

    def serve(self):
        self.socket.bind((my_ip(), 12345))
        self.socket.listen(1)
        self.socket, addr = self.socket.accept()
        self.inject_line("SRV: kapcsolat innen: " + addr)

        hasher = hashlib.sha1()
        psw = b""
        while psw[-5:] != b"ROGER":
            psw += self.socket.recv(1024)
        hasher.update(psw[:-5])
        theirhash = hasher.digest()

    def authenticate(self, event=None):
        del event
        hasher = hashlib.sha1()
        pw = self.entry.get()
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
            while msg[-5:] != b"ROGER" and self.running:
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
