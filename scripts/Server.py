import socket
import pickle
import sys
import time
import JogoDaMemoria as jm

def verificaDimensao(dim):
  if dim % 2 != 0:
    print("A dimensao do tabuleiro deve ser par.")
    return False
  if dim < 4 or dim > 10:
    print("A dimensao do tabuleiro deve estar entre 4 e 10.")
    return False
  return True

   
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
    lista_jogadas = self.recebe_msg(jogador=self.jogadorDaVez)
    i1, j1 = lista_jogadas[0], lista_jogadas[1]
    i2, j2 = lista_jogadas[2], lista_jogadas[3]
    # Pecas escolhidas sao iguais?
    tabuleiro_atualizado = self.tabuleiro
    tabuleiro_atualizado[i1][j1] = -tabuleiro_atualizado[i1][j1]
    tabuleiro_atualizado[i2][j2] = -tabuleiro_atualizado[i2][j2]
    self.enviaTabuleiro(tabuleiro_atualizado),
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
    self.placar = vencedores
    if len(vencedores) > 1:

        sys.stdout.write("Houve empate entre os jogadores ")
        for i in vencedores:
            sys.stdout.write(str(i + 1) + ' ')
        sys.stdout.write("\n")
        
    else:
        print("Jogador {0} foi o vencedor!".format(vencedores[0] + 1))
    self.atualizaStatusJogadores()

  def inicializaPortas(self):
    print("Inicializando sockets")
    for i in range(self.nJogadores):
      porta = self.PORTA_BASE + i
      print(f"PORTA: {porta}")
      conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      #print(f"CONEXÃO: {conexao}")
      conexao.settimeout(None)
      conexao.bind((self.HOST, porta))
      #print("BIND FEITO")
      conexao.listen()
      #print("LISTEN FEITO")
      con, endereco = conexao.accept()
      print(con)
      self.lista_sockets.append(con)
      print(self.lista_sockets)
      print(f"O Jogador {i+1} foi conectado\n")
  
    self.ativo = True
    return self.lista_sockets

  def enviaTabuleiro(self, tabuleiro):
     for i in range(self.nJogadores):
        print(f"Enviando atualização do tabuleiro para o Jogador {i+1}...")
        servidor.envia_msg(tabuleiro, i)
        print("Atualização enviada com sucesso!\n")

  def recebe_msg(self, jogador):
    while True:
      msg = pickle.loads(self.jogadores[jogador].recv(1024))
      if msg != None:
        break	
    return msg
  
  def envia_msg(self, msg, jogador):
    self.jogadores[jogador].send(pickle.dumps(msg))
    time.sleep(0.2)
  
  def atualizaStatusJogadores(self):
    for i in range(len(self.jogadores)):
      self.envia_msg(self.ativo, i) # envia status do jogo
      self.envia_msg(self.jogadorDaVez, i) # envia jogador da vez
      self.envia_msg(self.tabuleiro, i) # envia tabuleiro inicial
      self.envia_msg(self.placar, i) # envia placar inicial

if __name__ == "__main__":
  print("[*] O Servidor foi iniciado")
  dim = int(input("Digite a dimensao do tabuleiro: "))

  while not verificaDimensao(dim):
    dim = int(input("A dimensão precisa ser maior que 4 e menor que 10 e par. Digite novamente: "))

  nJogadores = int(input("Digite o numero de jogadores: "))

  while nJogadores < 2 or nJogadores > 6:
    nJogadores = int(input("O número de jogadores precisa ser maior que 2 e menor que 6. Digite novamente: "))

  servidor = ServidorJogoMemoria(dim, nJogadores)
  print("startando o jogo...")
  tabuleiro = jm.novoTabuleiro(4)



  for i in range(len(servidor.jogadores)):
    servidor.envia_msg(i, i) # envia id do jogador
  servidor.atualizaStatusJogadores()
  
  print(servidor.ativo)

  while servidor.ativo:
     print(f"Jogador atual: {servidor.jogadorDaVez + 1}")
     #servidor.enviaTabuleiro()
     print(f"Aguando o jogador {servidor.jogadorDaVez+1} escolher")
     servidor.verificaJogada()
     #servidor.enviaTabuleiro()
     servidor.atualizaStatusJogadores()
  servidor.verificaVencedor()
  servidor.finalizaServidor()