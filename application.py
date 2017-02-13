import time
import socket
import hashlib
import datetime

from tkinter import *
from tkinter import messagebox as tkmb

from Crypto.Cipher import AES

MAXLINE = 20


class Application(Tk):

    def __init__(self):
        super(Application, self).__init__()

        self.protocol("WM_DELETE_WINDOW", self.teardown)

        self.pwhash = None
        self.crypto = None
        self.msocket = None
        self.running = True
        self.connected = False
        self.cache = []

        self.label = Label(self, text="Inicializálás...")
        self.label.pack(fill=BOTH)
        fr = Frame(self)
        fr.pack()
        self.display = Text(fr, width=80, height=MAXLINE, wrap="word")
        self.display.pack(side=RIGHT)
        self.display.insert(END, "Kérem szépen a jelszót!")

        self.entry = Entry(self, show="*")
        self.entry.bind("<Return>", self.authenticate)
        self.entry.pack(fill=BOTH)

    def inject_line(self, line):
        line = line.strip()
        now = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"\n{now} - {line}"
        self.display.insert(END, line)
        self.display.see(END)

    def set_label(self, txt):
        self.label.configure(text=txt)

    def authenticate(self, event=None):
        del event
        hasher = hashlib.sha1()
        pw = self.entry.get()
        if not pw:
            return
        hasher.update(pw.encode())
        self.pwhash = hasher.digest()
        self.crypto = AES.new(self.pwhash[:16])

        self.entry.delete(0, END)
        self.entry.configure(show="")
        self.entry.unbind("<Return>")
        self.entry.bind("<Return>", self.message)

    def listen(self):
        print("Listener starting...")
        while self.running:
            crypt = b""
            while crypt[-5:] != b"ROGER" and self.running:
                try:
                    crypt += self.msocket.recv(1024)
                except socket.timeout:
                    pass
                time.sleep(0.1)
            msg = self.decrypt(crypt[:-5]).decode("utf8")
            if msg == "SHUTDOWN":
                msg = "Kilépett!"
            self.inject_line("Ő: " + msg)
        print("Listener nice exit!")

    def send_messages(self):
        while self.running:
            time.sleep(0.5)
            if not self.cache:
                continue
            msg = self.cache.pop(0)
            crypt = self.encrypt(msg)
            self.msocket.sendall(crypt + b"ROGER")
            self.inject_line("ÉN: " + msg)
        print("Sender nice exit!")

    def message(self, event=None):
        del event
        self.cache.append(self.entry.get())
        self.entry.delete(0, END)
        self.entry.focus_set()

    def teardown(self):
        print("Received Teardown command")
        self.running = False
        for i in range(3, 0, -1):
            time.sleep(1)
            self.label.config(text=f"Kilépés... {i}")
        if self.msocket is not None:
            self.msocket.close()
        self.destroy()

    def encrypt(self, msg):
        msg = msg.encode()
        slices = [msg[start:start+16] for start in range(0, len(msg), 16)]
        slices[-1] += b" " * (16 - len(slices[-1]))
        cslices = (self.crypto.encrypt(slc) for slc in slices)
        return b"".join(cslices)

    def decrypt(self, crypto):
        slices = [crypto[start:start+16] for start in range(0, len(crypto), 16)]
        mslices = (self.crypto.decrypt(slc) for slc in slices)
        return b"".join(mslices).strip()
