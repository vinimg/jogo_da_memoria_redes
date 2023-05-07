import socket
from time import sleep
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
   
  def recebe_msg(self):
    while True:
      msg = pickle.loads(self.socket.recv(1024))
      if msg != None:
        break	
    return msg
  
  def envia_msg(self, msg):
    self.socket.send(pickle.dumps(msg))

  def solicitaEscolhaPeca(self): # CLIENTE
    while True:

        # Imprime status do jogo
        jm.imprimeStatus(self.tabuleiro, self.placar, self.idJogador) # CLIENTE

        # Solicita coordenadas da primeira peca.
        coordenadas = jm.leCoordenada(len(self.tabuleiro)) # CLIENTE
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
  PORTA = 9300
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

  ativo = pickle.loads(socketClient.recv(1024))
  print(ativo)
  idJogador = pickle.loads(socketClient.recv(1024))
  print(idJogador)
  jogadorDaVez = pickle.loads(socketClient.recv(1024))
  print(jogadorDaVez)
  tabuleiro = pickle.loads(socketClient.recv(1024))
  print(tabuleiro)
  placar = pickle.loads(socketClient.recv(1024))
  print(placar)
  client = Cliente(socketClient, tabuleiro, placar, jogadorDaVez, idJogador, ativo)

  sleep(1)

  while client.ativo:
    if client.jogadorDaVez == client.idJogador:
      listaPosPecas = [0, 0, 0, 0]
      listaPosPecas[0], listaPosPecas[1] = client.solicitaEscolhaPeca()
      listaPosPecas[2], listaPosPecas[3] = client.solicitaEscolhaPeca()
      client.envia_msg(listaPosPecas)
      ativo = client.recebe_msg()
      print(ativo)
      jogadorDaVez = client.recebe_msg()
      print(jogadorDaVez)
      tabuleiro = client.recebe_msg()
      placar = client.recebe_msg()
      jm.imprimeStatus(tabuleiro, placar, idJogador)
    else:
      print(type(client.jogadorDaVez))
      print(f"O jogador {client.jogadorDaVez + 1} está fazendo sua jogada")
  client.socket.close()
