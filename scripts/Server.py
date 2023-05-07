import socket
import pickle
import sys
import time
import JogoDaMemoria as jm


class ServidorJogoMemoria:
  def __init__(self, dim, nJogadores, totalDePares):
    
    self.HOST = '127.0.0.1'
    self.PORTA_BASE = 9095
    self.lista_sockets = []
    self.ativo = False
    self.dim = dim #SERVIDOR
    self.nJogadores = nJogadores #SERVIDOR
    self.totalDePares = totalDePares #SERVIDOR
    self.tabuleiro = jm.novoTabuleiro(dim) #SERVIDOR E CLIENTE
    self.placar = jm.novoPlacar(nJogadores) #SERVIDOR E CLIENTE
    self.paresEncontrados = 0 #SERVIDOR
    self.jogadores = self.inicializaPortas()
    self.jogadorDaVez = 0

    for i in range(nJogadores): # teste
      print(self.jogadores[i].recv(1024).decode())

  def finalizaServidor(self):
    #encerra conexoes
    for p in self.jogadores:
      p.close()

  def verificaJogada(self):
    lista_jogadas = pickle.loads(self.lista_sockets[self.jogadorDaVez].recv(1024))
    i1, j1 = lista_jogadas[0], lista_jogadas[1]
    i2, j2 = lista_jogadas[2], lista_jogadas[3]
    # Pecas escolhidas sao iguais?
    if self.tabuleiro[i1][j1] == self.tabuleiro[i2][j2]: # SERVIDOR

        print("Pecas casam! Ponto para o jogador {0}.".format(self.jogadorDaVez + 1))
        
        jm.incrementaPlacar(self.placar, self.jogadorDaVez)
        self.paresEncontrados = self.paresEncontrados + 1
        jm.removePeca(self.tabuleiro, i1, j1)
        jm.removePeca(self.tabuleiro, i2, j2)
        if self.paresEncontrados >= self.totalDePares:
           self.ativo = False

        time.sleep(5)
    else:

        print("Pecas nao casam!")
        
        time.sleep(3)

        jm.fechaPeca(self.tabuleiro, i1, j1)
        jm.fechaPeca(self.tabuleiro, i2, j2)
        self.jogadorDaVez = (self.jogadorDaVez + 1) % self.nJogadores
    
  def verificaVencedor(self):
    # Verificar o vencedor e imprimir
    pontuacaoMaxima = max(self.placar)
    vencedores = []
    for i in range(0, self.nJogadores):

        if self.placar[i] == pontuacaoMaxima:
            vencedores.append(i)

    if len(vencedores) > 1:

        sys.stdout.write("Houve empate entre os jogadores ")
        for i in vencedores:
            sys.stdout.write(str(i + 1) + ' ')

        sys.stdout.write("\n")
        self.ativo = False

    else:

        print("Jogador {0} foi o vencedor!".format(vencedores[0] + 1))
        self.ativo = False

  def inicializaPortas(self):
    for i in range(self.nJogadores):
      porta = self.PORTA_BASE + i
      conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      conexao.bind((self.HOST, porta))
      conexao.listen()
      con, endereco = conexao.accept()
      self.lista_sockets.append(con)
      print(f"O Jogador {i+1} foi conectado\n")
  
    self.ativo = True
    return self.lista_sockets

  def enviaTabuleiro(self):
     for i in range(self.nJogadores):
        print(f"Enviando atualização do tabuleiro para o Jogador {i+1}...")
        servidor.lista_sockets[i].send(pickle.dumps(self.tabuleiro))
        print("Atualização enviada com sucesso!\n")

  def atualizaStatusJogadores(self):
    for i in range(len(servidor.jogadores)):
      servidor.jogadores[i].send(str(self.ativo).encode()) # envia status do jogo
      servidor.jogadores[i].send(str(self.jogadorDaVez).encode()) # envia jogador da vez
      servidor.jogadores[i].send(pickle.dumps(self.tabuleiro)) # envia tabuleiro inicial
      servidor.jogadores[i].send(pickle.dumps(self.placar)) # envia placar inicial

if __name__ == "__main__":
  print("[*] O Servidor foi iniciado")
  # testes
  servidor = ServidorJogoMemoria(1, 2, 8)

  tabuleiro = jm.novoTabuleiro(4)
  for i in range(len(servidor.jogadores)):
    servidor.jogadores[i].send(str(True).encode()) # envia status do jogo
    servidor.jogadores[i].send(str(i).encode()) # envia id do jogador
    servidor.jogadores[i].send(str(0).encode) # envia jogador inicial
    servidor.jogadores[i].send(pickle.dumps(tabuleiro)) # envia tabuleiro inicial
    servidor.jogadores[i].send(pickle.dumps(servidor.placar)) # envia placar inicial
  
  print(servidor.ativo)

  while servidor.ativo:
     print(f"Jogador atual: {servidor.jogadorDaVez}")
     servidor.enviaTabuleiro()
     for i in range(servidor.nJogadores):
      print(f"Aguando o jogador {i+1} escolher")
      servidor.atualizaStatusJogadores()
      servidor.verificaJogada()
      servidor.verificaVencedor()
      servidor.atualizaStatusJogadores()

  servidor.finalizaServidor()