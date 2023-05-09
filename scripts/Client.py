import socket
from time import sleep
import pickle
import re
import JogoDaMemoria as jm

def valida_ip(ip):
  # Valida se o input do usuario eh valido
    padrao = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    match = re.match(padrao, ip)
    if not match:
        return False
    octetos = [int(octeto) for octeto in match.groups()]
    if any(octeto > 255 for octeto in octetos):
        return False
    return True

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
  def recebe_status_jogadores(self):
    self.ativo = self.recebe_msg()
    self.jogadorDaVez = self.recebe_msg()
    self.tabuleiro = self.recebe_msg()
    self.placar = self.recebe_msg()
    #print(f"tabuleiro = {self.tabuleiro};\n placar = {self.placar};\n jogadorDaVez = {self.jogadorDaVez};\n ativo = {self.ativo}") # debug

  def envia_msg(self, msg):
    self.socket.send(pickle.dumps(msg))
    sleep(0.2)

  def recebe_tabuleiro(self):
    self.tabuleiro = self.recebe_msg()
    jm.imprimeTabuleiro(self.tabuleiro)
    print(f"\n --Jogada do jogador {self.jogadorDaVez + 1}--")
    sleep(2.5)
  
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
  HOST = input("Digite o IP do servidor: ")
  while not valida_ip(HOST):
    print("IP inválido!")
    HOST = input("Digite o IP do servidor: ")
  
  while True:
    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    socketClient.settimeout(None)
    try:
      print(f"tentando conexao na porta {PORTA}")
      socketClient.connect((HOST, PORTA))
      print(f"conexao ok - {PORTA}")
      break
    except Exception as e:
      PORTA += 1

  idJogador = pickle.loads(socketClient.recv(1024))
  ativo = pickle.loads(socketClient.recv(1024))
  #print(f"idj = {idJogador} ativo = {ativo}") # debug
  jogadorDaVez = pickle.loads(socketClient.recv(1024))
  tabuleiro = pickle.loads(socketClient.recv(1024))
  placar = pickle.loads(socketClient.recv(1024))

  client = Cliente(socketClient, tabuleiro, placar, jogadorDaVez, idJogador, ativo)

  #sleep(1)

  while client.ativo:
    #print("JDV: " + str(client.jogadorDaVez + 1)) #debug
    jm.imprimeStatus(client.tabuleiro, client.placar, client.jogadorDaVez)
    if client.jogadorDaVez == client.idJogador:
      listaPosPecas = [0, 0, 0, 0]
      listaPosPecas[0], listaPosPecas[1] = client.solicitaEscolhaPeca()
      listaPosPecas[2], listaPosPecas[3] = client.solicitaEscolhaPeca()
      client.envia_msg(listaPosPecas)
      client.recebe_tabuleiro()
      client.recebe_status_jogadores()
      jm.imprimeStatus(client.tabuleiro, client.placar, client.jogadorDaVez)
    else:
      print(f"O jogador {client.jogadorDaVez + 1} está fazendo sua jogada")
      print("Aguarde sua vez...")
      client.recebe_tabuleiro()
      client.recebe_status_jogadores()
      jm.imprimeStatus(client.tabuleiro, client.placar, client.jogadorDaVez)
 
  # fim do jogo
  client.recebe_status_jogadores()
  vencedores = client.placar()

  if len(vencedores) > 1:

    print("Houve empate entre os jogadores")
    for i in vencedores:
        print(" " + str(i + 1), end="")
    print(".")

  else:
      print("Jogador {0} foi o vencedor!".format(vencedores[0] + 1))
  client.socket.close()
