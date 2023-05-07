import socket
from time import sleep
import pickle
import JogoDaMemoria as jm

PORTA_INICIAL = 9095
NUM_JOGADORES = 6
clientes = []
for i in range(NUM_JOGADORES): # apenas pra teste, na prática será um cliente por jogador
  HOST = '26.84.232.20'
  porta = PORTA_INICIAL
  while True:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      client.connect((HOST, porta))
      print(f"conexao ok - {porta}")
      break
    except Exception as e:
      print(e)
      porta += 1
  
  clientes.append(client)
  sleep(1)

  
for it in range(NUM_JOGADORES):
  clientes[it].send(f"hello from p{it}".encode())

print("aguardando tab")
tab = pickle.loads(clientes[0].recv(1024))
jm.imprimeTabuleiro(tab)