import socket
import pickle
import sys
import time
import JogoDaMemoria as jm


class ServidorJogoMemoria:
  def __init__(self, dim, nJogadores):
    
    self.HOST = '127.0.0.1'
    self.PORTA_BASE = 9300
    self.lista_sockets = []
    self.ativo = False
    self.dim = dim #SERVIDOR
    self.nJogadores = nJogadores #SERVIDOR
    self.totalDePares = dim**2/2 #SERVIDOR
    self.tabuleiro = jm.novoTabuleiro(dim) #SERVIDOR E CLIENTE
    self.placar = jm.novoPlacar(nJogadores) #SERVIDOR E CLIENTE
    self.paresEncontrados = 0 #SERVIDOR
    self.jogadores = self.inicializaPortas()
    print("Jogadores conectados.")
    self.jogadorDaVez = 0

  def finalizaServidor(self):
    #encerra conexoes
    for p in self.jogadores:
      p.close()

  def verificaJogada(self):
    lista_jogadas = pickle.loads(self.lista_sockets[self.jogadorDaVez].recv(1024))
    i1, j1 = lista_jogadas[0], lista_jogadas[1]
    i2, j2 = lista_jogadas[2], lista_jogadas[3]
    # Pecas escolhidas sao iguais?
    input("calma")
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
        servidor.envia_msg(self.tabuleiro, i)
        print("Atualização enviada com sucesso!\n")

  def recebe_msg(self):
    while True:
      msg = pickle.loads(self.socket.recv(1024))
      if msg != None:
        break	
    return msg
  
  def envia_msg(self, msg, jogador):
    self.jogadores[jogador].send(pickle.dumps(msg))
    time.sleep(0.1)
  
  def atualizaStatusJogadores(self):
    for i in range(len(self.jogadores)):
      self.envia_msg(self.ativo, i) # envia status do jogo
      self.envia_msg(self.jogadorDaVez, i) # envia jogador da vez
      self.envia_msg(self.tabuleiro, i) # envia tabuleiro inicial
      self.envia_msg(self.placar, i) # envia placar inicial

if __name__ == "__main__":
  print("[*] O Servidor foi iniciado")
  # testes
  servidor = ServidorJogoMemoria(dim=4, nJogadores=1)
  print("startando o jogo...")
  tabuleiro = jm.novoTabuleiro(4)

  for i in range(len(servidor.jogadores)):
    servidor.envia_msg(True, i) # envia status do jogo
    servidor.envia_msg(i, i) # envia id do jogador
    servidor.envia_msg(0, i) # envia jogador inicial
    servidor.envia_msg(tabuleiro, i) # envia tabuleiro inicial
    print(servidor.placar)
    servidor.envia_msg(servidor.placar, i) # envia placar inicial
  
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