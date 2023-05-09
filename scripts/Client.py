import socket
from time import sleep
import pickle
import re
import JogoDaMemoria as jm

#################### FUNCOES E CLASSE ####################

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

  def __init__(self,  socket, tabuleiro, placar, jogador_da_vez, id_jogador, ativo):
    self.socket = socket
    self.tabuleiro = tabuleiro
    self.placar = placar
    self.jogador_da_vez = jogador_da_vez
    self.id_jogador = id_jogador
    self.ativo = ativo
   
  def recebe_msg(self):
    # recebe uma informacao do servidor
    while True:
      msg = pickle.loads(self.socket.recv(1024))
      if msg != None:
        break	
    return msg
  
  def recebe_status_jogadores(self):
    # equivalente da funcao envia_status_jogadores do servidor
    self.ativo = self.recebe_msg()
    self.jogador_da_vez = self.recebe_msg()
    self.tabuleiro = self.recebe_msg()
    self.placar = self.recebe_msg()

  def envia_msg(self, msg):
    # envia uma informacao ao servidor
    self.socket.send(pickle.dumps(msg))
    sleep(0.2)

  def recebe_tabuleiro(self):
    # equivalente da funcao envia_tabuleiro do servidor
    self.tabuleiro = self.recebe_msg()
    jm.imprimeTabuleiro(self.tabuleiro)
    print(f"\n -- Jogada do jogador {self.jogador_da_vez + 1} --")
    sleep(2.5)
  
  def solicita_escolha_pecas(self):
    # Pede a jogada ao jogador
    while True:
        # Imprime status do jogo
        jm.imprimeStatus(self.tabuleiro, self.placar, self.id_jogador) # CLIENTE

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


#################### MAIN ####################
if __name__ == "__main__":
  PORTA_BASE = 9300

  HOST = input("Digite o IP do servidor: ")
  while not valida_ip(HOST):
    print("IP inválido!")
    HOST = input("Digite o IP do servidor: ")
  
  # Tentando conexao com o servidor
  porta =  PORTA_BASE
  while True:
    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    socketClient.settimeout(None)
    try:
      print(f"Tentando conexao na porta {porta}")
      socketClient.connect((HOST, porta))
      print(f"Conexao ok - porta:{porta}")
      break
    except Exception as e:
      porta += 1
      if porta - PORTA_BASE > 5:
         print("Conexao com o servidor falhou. Garanta que o servidor está rodando e rode o cliente novamente")
         sleep(2)
         quit()

  # recebendo informacoes iniciais do servidor
  idJogador = pickle.loads(socketClient.recv(1024))
  ativo = pickle.loads(socketClient.recv(1024))
  jogadorDaVez = pickle.loads(socketClient.recv(1024))
  tabuleiro = pickle.loads(socketClient.recv(1024))
  placar = pickle.loads(socketClient.recv(1024))
  client = Cliente(socketClient, tabuleiro, placar, jogadorDaVez, idJogador, ativo)

  while client.ativo:
    jm.imprimeStatus(client.tabuleiro, client.placar, client.jogador_da_vez)
    if client.jogador_da_vez == client.id_jogador:
      listaPosPecas = [0, 0, 0, 0]
      listaPosPecas[0], listaPosPecas[1] = client.solicita_escolha_pecas()
      listaPosPecas[2], listaPosPecas[3] = client.solicita_escolha_pecas()
      client.envia_msg(listaPosPecas)
      client.recebe_tabuleiro()
      client.recebe_status_jogadores()
      jm.imprimeStatus(client.tabuleiro, client.placar, client.jogador_da_vez)
    else:
      print(f"O jogador {client.jogador_da_vez + 1} está fazendo sua jogada")
      print("Aguarde sua vez...")
      client.recebe_tabuleiro()
      client.recebe_status_jogadores()
      jm.imprimeStatus(client.tabuleiro, client.placar, client.jogador_da_vez)
 
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
