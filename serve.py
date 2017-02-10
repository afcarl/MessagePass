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
        print("REMOTE: {msg}".format(msg=msg[:-5].decode("utf8")))
    print("Listener exiting...")

# Initialize
hasher = hashlib.sha1()
connme = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connme.bind((HIM, 12345))

# Wait for incoming
connme.listen(1)
print("Awaiting connection...")
hasher.update(input("PWD > ").encode())
phash = hasher.digest()
try:
    useme, remote = connme.accept()
    print("Connection form {}".format(remote))
finally:
    connme.close()

# Authenticate

hasher = hashlib.sha1()
rhash = b""
while rhash[-5:] != b"ROGER":
    rhash += useme.recv(1024)
rhash = rhash[:-5]

if phash != rhash:
    useme.sendall(b"SODOFFROGER")
    raise RuntimeError("Can't establish!")

print("Client authenticated!")
useme.sendall(b"OKROGER")
time.sleep(1)

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
