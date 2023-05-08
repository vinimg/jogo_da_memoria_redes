#Create an ipv4 socket and listen for incoming connections
import json
import socket
import JogoDaMemoria as jm

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

tabuleiro = jm.novoTabuleiro(4)
print(tabuleiro)

#Receive the data
while True:
	data = (client_socket.recv(1024)).decode()
	
	if not data:
		break
	print(f'[+] {address} sent: {data}')
	
	# Codificar a lista em formato JSON
	lista_encoded = json.dumps(tabuleiro).encode()
	client_socket.sendall(lista_encoded)
#Close the connection
client_socket.close()
server.close()



