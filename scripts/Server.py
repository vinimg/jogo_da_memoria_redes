import socket
import pickle
import sys
import time
import JogoDaMemoria as jm

############# FUNCOES E CLASSE #############
def verifica_dimensao(dim):
  if dim % 2 != 0:
    print("A dimensao do tabuleiro deve ser par.")
    return False
  if dim < 4 or dim > 10:
    print("A dimensao do tabuleiro deve estar entre 4 e 10.")
    return False
  return True

   
class ServidorJogoMemoria:
  def __init__(self, dim, n_jogadores):
    
    self.HOST = '127.0.0.1'
    self.PORTA_BASE = 9300
    self.lista_sockets = []
    self.ativo = False
    self.dim = dim #SERVIDOR
    self.n_jogadores = n_jogadores #SERVIDOR
    self.total_de_pares = dim**2/2 #SERVIDOR
    self.tabuleiro = jm.novoTabuleiro(dim) #SERVIDOR E CLIENTE
    self.placar = jm.novoPlacar(n_jogadores) #SERVIDOR E CLIENTE
    self.pares_encontrados = 0 #SERVIDOR
    self.jogadores = self.inicializa_portas()
    print("[*] Jogadores conectados.")
    self.jogador_da_vez = 0

  def finaliza_servidor(self):
    #encerra conexoes
    for p in self.jogadores:
      p.close()

  def verifica_jogada(self):
    # Avalia a jogada feita pelo jogador da vez
    lista_jogadas = self.recebe_msg(jogador=self.jogador_da_vez)
    i1, j1 = lista_jogadas[0], lista_jogadas[1]
    i2, j2 = lista_jogadas[2], lista_jogadas[3]
    # Pecas escolhidas sao iguais?
    tabuleiro_atualizado = self.tabuleiro
    tabuleiro_atualizado[i1][j1] = -tabuleiro_atualizado[i1][j1]
    tabuleiro_atualizado[i2][j2] = -tabuleiro_atualizado[i2][j2]
    # mostra a jogada do jogador da vez para todos os jogadores
    self.envia_tabuleiro(tabuleiro_atualizado)

    if self.tabuleiro[i1][j1] == self.tabuleiro[i2][j2]:
        # caso pecas casem
        print("Pecas casam! Ponto para o jogador {0}.".format(self.jogador_da_vez + 1))
        jm.incrementaPlacar(self.placar, self.jogador_da_vez)
        self.pares_encontrados = self.pares_encontrados + 1
        jm.removePeca(self.tabuleiro, i1, j1)
        jm.removePeca(self.tabuleiro, i2, j2)
        if self.pares_encontrados >= self.total_de_pares: # condicao de parada do jogo
           self.ativo = False
        time.sleep(3)
    else:
        # caso pecas nao casam
        print("Pecas nao casam!")
        time.sleep(3)
        jm.fechaPeca(self.tabuleiro, i1, j1)
        jm.fechaPeca(self.tabuleiro, i2, j2)
        self.jogador_da_vez = (self.jogador_da_vez + 1) % self.n_jogadores
    
  def verifica_vencedor(self):
    # Verificar o vencedor e imprimir
    pontuacaoMaxima = max(self.placar)
    vencedores = []
    for i in range(0, self.n_jogadores):

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
    self.atualiza_status_jogadores()

  def inicializa_portas(self):
    # Inicializa os sockets, conecta os jogadores e retorna a lista de sockets
    print("[*] Inicializando sockets")
    for i in range(self.n_jogadores):
      porta = self.PORTA_BASE + i
      conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      conexao.settimeout(None)
      conexao.bind((self.HOST, porta))
      conexao.listen()
      con, endereco = conexao.accept()
      self.lista_sockets.append(con)
      print(self.lista_sockets)
      print(f"[*] O Jogador {i+1} foi conectado\n")
  
    self.ativo = True
    return self.lista_sockets

  def envia_tabuleiro(self, tabuleiro):
     # envia o tabuleiro para todos os jogadores
     for i in range(self.n_jogadores):
        print(f"Enviando atualização do tabuleiro para o Jogador {i+1}...")
        servidor.envia_msg(tabuleiro, i)
        print("Atualização enviada com sucesso!\n")

  def recebe_msg(self, jogador):
    # recebe uma informacao da socket do jogador especificado
    while True:
      msg = pickle.loads(self.jogadores[jogador].recv(1024))
      if msg != None:
        break	
    return msg
  
  def envia_msg(self, msg, jogador):
    # envia uma informacao ao jogador especificado
    self.jogadores[jogador].send(pickle.dumps(msg))
    time.sleep(0.2)
  
  def atualiza_status_jogadores(self):
    # envia informacoes a todos os jogadores
    for i in range(len(self.jogadores)):
      self.envia_msg(self.ativo, i) # envia status do jogo
      self.envia_msg(self.jogador_da_vez, i) # envia jogador da vez
      self.envia_msg(self.tabuleiro, i) # envia tabuleiro inicial
      self.envia_msg(self.placar, i) # envia placar inicial


#################### MAIN ####################
if __name__ == "__main__":
  print("[*] O Servidor foi iniciado")
  dim = int(input("Digite a dimensao do tabuleiro: "))

  while not verifica_dimensao(dim):
    dim = int(input("A dimensão precisa ser maior que 4 e menor que 10 e par. Digite novamente: "))

  n_jogadores = int(input("Digite o numero de jogadores: "))

  while n_jogadores < 2 or n_jogadores > 6:
    n_jogadores = int(input("O número de jogadores precisa ser maior que 2 e menor que 6. Digite novamente: "))

  servidor = ServidorJogoMemoria(dim, n_jogadores)
  tabuleiro = jm.novoTabuleiro(4)



  for i in range(len(servidor.jogadores)):
    servidor.envia_msg(i, i) # envia id do jogador
  servidor.atualiza_status_jogadores()
  
  print(servidor.ativo)

  while servidor.ativo:
     print(f"Jogador atual: {servidor.jogador_da_vez + 1}")
     print(f"Aguando o jogador {servidor.jogador_da_vez+1} escolher")
     servidor.verifica_jogada()
     servidor.atualiza_status_jogadores()
  # fim do jogo
  servidor.verifica_vencedor()
  servidor.finaliza_servidor()