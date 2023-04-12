import socket
import random
from time import sleep
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address="localhost"
port=12345
s.bind((address, port))
s.listen(1)
conn,addr=s.accept()
print("Connection established")
l=[1,0,45,0]
while True:
    l=[l[i]+random.randint(-100,100)/100 for i in range(4)]
    conn.send(str(l).encode("utf-8"))
    # print(conn.recv(1024).decode())
    # sleep(0.01)

# conn.send(str([1.0,0.0,45.0,0.0]).encode("utf-8"))