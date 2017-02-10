import time
import socket
import hashlib
import threading as thr

HIM = "127.0.0.1"
running = True

def listen(sck):
    print("Listener starting...")
    while running:
        msg = b""
        while msg[-5:] != b"ROGER" and running:
            msg += sck.recv(1024)
            time.sleep(0.1)
        print("\nREMOTE: {msg}>\n ".format(msg=msg[:-5].decode("utf8")))
    print("Listener exiting...")

# Initialize
hasher = hashlib.sha1()
address = socket.gethostbyname(socket.gethostname())
useme = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
useme.connect((HIM, 12345))
print("Connected to", HIM)

# Authenticate
hasher.update(input("PSSW > ").encode())
phash = hasher.digest()
useme.sendall(phash + b"ROGER")
time.sleep(1)

answ = b""
while answ[-5:] != b"ROGER":
    answ += useme.recv(1024)
    time.sleep(0.1)
answ = answ[:-5].decode("utf8")
if answ == "SODOFF":
    raise RuntimeError("Azonosítás sikertelen!")

# Launch main loops
listener = thr.Thread(target=listen, args=(useme,))
listener.start()
while 1:
    sendme = input("> ").encode() + b"ROGER"
    if sendme == b"off":
        break
    useme.sendall(sendme)

# Teardown
running = False
print("Shutting down...")
time.sleep(10)
print("1")
