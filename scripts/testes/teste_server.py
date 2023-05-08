import socket
import pickle
import JogoDaMemoria as jm


class gerenciador_jogadores:
  def __init__(self, num_jogadores):
    self.jogadores = self.inicializa_portas(num_jogadores)

    for i in range(num_jogadores): # teste
      print(self.jogadores[i].recv(1024).decode())

  def finaliza(self):
    #encerra conexoes
    for p in self.jogadores:
      p.close()
  
  def inicializa_portas(self, num_jogadores):
    # inicializa as portas para os jogadores e retorna uma lista de conexoes
    HOST = '127.0.0.1'
    PORTA_BASE = 9095
    lista = []
    for i in range(num_jogadores):
      porta = PORTA_BASE + i
      conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      conexao.bind((HOST, porta))
      conexao.listen()
      con, endereco = conexao.accept()
      lista.append(con)
    return lista

      
# testes
p = gerenciador_jogadores(6)

tab = jm.novoTabuleiro(4)
print("enviando tab")
p.jogadores[0].send(pickle.dumps(tab)) # pickle converte a lista em bytes
print("tab enviado")

p.finaliza()