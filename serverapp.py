import socket
import threading as thr
import time
from tkinter import messagebox as tkmb

from application import Application, PORT

HER = "127.0.0.1"
ME = "127.0.0.1"


class MsgServer(Application):

    def __init__(self):
        super(MsgServer, self).__init__()
        self.title("Szerver")
        self.connector = thr.Thread(target=self.connect)
        self.listener = thr.Thread(target=self.listen)
        self.sender = thr.Thread(target=self.send_messages)

        self.connector.start()

    def connect(self):
        csocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        csocket.settimeout(1)
        csocket.bind((ME, PORT))

        self.set_label("Várakozás kapcsolatra...")
        csocket.listen(1)
        while self.running:
            try:
                self.msocket, addr = csocket.accept()
            except socket.timeout:
                pass
            else:
                if addr[0] != HER:
                    tkmb.showwarning("Ajjaj", f"Bejövő cím: {HER} helyett {addr[0]}")
                csocket.close()
                break
        else:
            print("Connector nice exit!")
            return
        self.msocket.settimeout(0.5)
        while self.pwhash is None:
            time.sleep(1)

        hsh = b""
        while hsh[-5:] != b"ROGER":
            try:
                hsh += self.msocket.recv(1024)
            except socket.timeout:
                pass
        if hsh[:-5] != self.pwhash:
            tkmb.showerror("Autentikációs hiba!")
            self.teardown()
            return
        self.msocket.sendall(b"OKROGER")

        self.connected = True
        self.listener.start()
        self.sender.start()
        print("Connector nice finish!")


if __name__ == '__main__':
    app = MsgServer()
    app.mainloop()
    print("Application nice exit!")
