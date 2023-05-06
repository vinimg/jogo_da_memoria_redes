#now create a client socket and connect to the server socket and send a 'hello world'
import socket
#Define the port and host
HOST = '127.0.0.1'
PORT = 9999
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send('hello world'.encode())
#Receive data from the server and shut down
response = client.recv(1024)
print(response.decode())
client.close()