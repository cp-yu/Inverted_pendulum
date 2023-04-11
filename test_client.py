import socket

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address="localhost"
port=12346
address=(address,int(port))
s.connect(address)


# host = "localhost"
# port = 12345
# address = (host, int(port))
# path = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# path.connect(address)
while   True:
    print(s.recv(1024).decode())