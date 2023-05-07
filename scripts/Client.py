import socket
from time import sleep
import sys
import os
import pickle
import JogoDaMemoria as jm

class Cliente:

  def __init__(self,  socket, tabuleiro, placar, jogadorDaVez, idJogador, ativo):
    self.socket = socket
    self.tabuleiro = tabuleiro
    self.placar = placar
    self.jogadorDaVez = jogadorDaVez
    self.idJogador = idJogador
    self.ativo = ativo
   
  def solicitaEscolhaPeca(self): # CLIENTE
    while True:

        # Imprime status do jogo
        jm.imprimeStatus(self.tabuleiro, self.placar, self.idJogador) # CLIENTE

        # Solicita coordenadas da primeira peca.
        coordenadas = jm.leCoordenada(self.idJogador) # CLIENTE
        if coordenadas == False:
            continue

        i, j = coordenadas

        # Testa se peca ja esta aberta (ou removida)
        if jm.abrePeca(self.tabuleiro, i, j) == False: # CLIENTE

            print("Escolha uma peca ainda fechada!")
            input("Pressione <enter> para continuar...")
            continue

        break
    return i, j


if __name__ == "__main__":
  PORTA = 9095
  NUM_JOGADORES = 6
  HOST = '127.0.0.1'
  while True:
    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    try:
      socketClient.connect((HOST, PORTA))
      print(f"conexao ok - {PORTA}")
      break
    except Exception as e:
      print(e)
      PORTA += 1

  ativo = socketClient.recv(1024).decode()
  print(ativo)
  idJogador = socketClient.recv(1024).decode()
  jogadorDaVez = socketClient.recv(1024).decode()
  tabuleiro = pickle.loads(socketClient.recv(1024))
  placar = pickle.loads(socketClient.recv(1024))

  client = Cliente(socketClient, tabuleiro, placar, jogadorDaVez, idJogador, ativo)
  sleep(1)

  while client.ativo:
    if client.jogadorDaVez == client.idJogador:
      listaPosPecas = [0, 0, 0, 0]
      listaPosPecas[0], listaPosPecas[1] = client.solicitaEscolhaPeca()
      listaPosPecas[2], listaPosPecas[3] = client.solicitaEscolhaPeca()
      client.socket.send(pickle.dumps(listaPosPecas))
    else:
      print(f"O jogador {client.vez + 1} está fazendo sua jogada")
      
    client.ativo = socketClient.recv(1024).decode()
    client.jogadorDaVez = int(socketClient.recv(1024).decode())
    client.tabuleiro = pickle.loads(socketClient.recv(1024))
    client.placar = pickle.loads(socketClient.recv(1024))
    jm.imprimeStatus(tabuleiro, placar, idJogador)
    
  client.socket.close()
