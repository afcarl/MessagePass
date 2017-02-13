import socket
import threading as thr
import time
from tkinter import messagebox as tkmb

from MessagePass.application import Application, PORT

HIM = "127.0.0.1"


class MsgClient(Application):

    def __init__(self):
        super(MsgClient, self).__init__()
        self.title("Kliens")

        self.msocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.msocket.settimeout(0.5)
        self.connector = thr.Thread(target=self.connect)
        self.listener = thr.Thread(target=self.listen)
        self.sender = thr.Thread(target=self.send_messages)

        self.connector.start()

    def connect(self):
        self.set_label("Várakozás kapcsolatra...")
        while self.running:
            try:
                self.msocket.connect((HIM, PORT))
            except ConnectionRefusedError:
                print("No server!")
                time.sleep(1)
            except socket.timeout:
                pass
            else:
                self.set_label("Kapcsolat felépítve")
                break
        else:
            print("Connector nice exit!")
            return

        while self.pwhash is None:
            time.sleep(1)
        self.msocket.sendall(self.pwhash + b"ROGER")

        msg = b""
        while msg[-5:] != b"ROGER":
            try:
                msg += self.msocket.recv(1024)
            except socket.timeout:
                pass
            time.sleep(0.1)
        if msg[:-5] == b"SODOFF":
            tkmb.showerror("Autentikációs hiba!", "Helytelen jelszó! Leállás...")
            self.teardown()
            return
        else:
            self.display.insert("end", "\nAutentikálva!")
            self.label.configure(text="Autentikálva")

        self.connected = True
        self.listener.start()
        self.sender.start()
        print("Connector nice finish!")


if __name__ == '__main__':
    app = MsgClient()
    app.mainloop()
    print("Application nice exit!")
