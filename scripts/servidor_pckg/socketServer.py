#Create an ipv4 socket and listen for incoming connections
import socket
#Define the port and host
HOST = '127.0.0.1'
PORT = 9999 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f'[*] Listening as {HOST}:{PORT}')
#Wait for a connection
client_socket, address = server.accept()
print(f'[+] {address} is connected.')
#Receive the data
while True:
	data = (client_socket.recv(1024)+'!!!!'.encode()).decode()
	if not data:
		break
	print(f'[+] {address} sent: {data}')
	#Send the data back to the client
	client_socket.send(data.encode())
#Close the connection
client_socket.close()
server.close()



