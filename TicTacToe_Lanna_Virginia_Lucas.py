import sys
import numpy as np
import threading
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, 
    QVBoxLayout, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt

#Classe que representa o tabuleiro
class Tabuleiro:
    #Criando tabuleiros auxiliares
    resultados = np.zeros((3, 3), dtype=int) #posições zeradas
    game_over_maior = False # variável de controle da finalização do tabuleiro maior
    finalizados = np.zeros((3, 3), dtype=int) #matriz de jogos finalizados

    def __init__(self, nome, ui_callback):
        #Criando o tabuleiro
        self.board = np.zeros((3, 3), dtype=int)
        self.game_over = False #flag de finalização do jogo
        self.nome = nome #número referente à posição do tabuleiro maior
        self.result = 0 #inicializando com nenhum vencedor
        self.ui_callback = ui_callback #referente ao funcionamento da interface

    #Fazendo a jogada
    def play(self, player):
        #Analisando se pode fazer a jogada
        while not self.game_over and not Tabuleiro.game_over_maior:
            x, y = np.random.randint(0, 3, 2) #gerar aleatoriamente as posições do tabuleiro menor
            print(f'Tabuleiro {self.nome} - Jogador {player} - Jogada nas coordenadas ({x},{y})')
            #Jogando
            if self.board[x, y] == 0: #se ainda não houve uma jogada nessa posição
                self.board[x, y] = player #a posição assume o rótulo do jogador
                self.ui_callback(self.nome, player, 0, x, y) #atualização da interface gráfica para o usuário
                print(f'Tabuleiro {self.nome} - Jogada realizada\n{self.board}')
            time.sleep(1)

    #Verificando se alguem ganhou nos mini jogos da velha
    def check_winner(self):
        #Analisando se ninguem já tinha ganhado no tabuleiro maior
        while not Tabuleiro.game_over_maior:
            #Analisando as linhas e as colunas
            for i in range(3):
                if np.all(self.board[i] == 1) or np.all(self.board[:, i] == 1): #linha/coluna inteira composta por uns
                    self.result = 1
                if np.all(self.board[i] == 2) or np.all(self.board[:, i] == 2): #linha/coluna inteira composta por dois
                    self.result = 2

            #Analisando as diagonais
            if np.all(np.diagonal(self.board) == 1) or np.all(np.diagonal(np.fliplr(self.board)) == 1): #diagonal de uns
                self.result = 1
            if np.all(np.diagonal(self.board) == 2) or np.all(np.diagonal(np.fliplr(self.board)) == 2): #diagonal de dois
                self.result = 2
            
            #Mostrando o resultado, se alguém ganhou
            if self.result in [1, 2]:
                self.game_over = True #finaliza aquele minijogo
                self.ui_callback(self.nome, self.result, 1, 0, 0) #atualiza o tabuleiro maior com a informação do jogador vencedor
                print(f'Tabuleiro {self.nome} - Jogador {self.result} ganhou!')
                Tabuleiro.resultados[divmod(self.nome, 3)] = self.result
                Tabuleiro.finalizados[divmod(self.nome, 3)] = 1
                Tabuleiro.check_maior(Tabuleiro.resultados) #solicita a conferência do tabuleiro maior
                break

            #Mostrando se for velha
            if np.all(self.board != 0):
                self.game_over = True #finaliza aquele minijogo
                self.ui_callback(self.nome, self.result, 1, 0, 0) #atualiza o tabuleiro maior mantendo a posição vazia
                print(f'Tabuleiro {self.nome} - Deu velha!')
                Tabuleiro.finalizados[divmod(self.nome, 3)] = 1
                Tabuleiro.check_maior(Tabuleiro.resultados) #solicita a conferência do tabuleiro maior
                break

    #Comecando o jogo
    def start(self):
        #Criando as threads
        self.j1 = threading.Thread(target=self.play, args=(1,)) #thread 1 como jogador 1
        self.j2 = threading.Thread(target=self.play, args=(2,)) #thread 2 como jogador 2
        self.conf = threading.Thread(target=self.check_winner) #thread de checagem de vencedores

        #Iniciando as threads
        self.j1.start()
        self.j2.start()
        self.conf.start()

    #Obtenção do resultado
    def resultado(self):
        self.j1.join()
        self.j2.join()
        self.conf.join()
        return self.result
    
    #Analisando se alguém ganhou no tabuleiro maior
    @staticmethod
    def check_maior(board_maior):
        result = 0 #inicia sem vencedores
        for i in range(3):
            #Checagem das linhas e colunas
            if np.all(board_maior[i] == 1) or np.all(board_maior[:, i] == 1): #linha/coluna inteira composta por uns
                result = 1
            if np.all(board_maior[i] == 2) or np.all(board_maior[:, i] == 2): #linha/coluna inteira composta por dois
                result = 2

        #Checagem das diagonais
        if np.all(np.diagonal(board_maior) == 1) or np.all(np.diagonal(np.fliplr(board_maior)) == 1): #diagonal inteira composta por uns
            result = 1
        if np.all(np.diagonal(board_maior) == 2) or np.all(np.diagonal(np.fliplr(board_maior)) == 2): #diagonal inteira composta por dois
            result = 2

        #Caso haja um vencedor (result == 1 ou result == 2)
        if result in [1, 2]:
           Tabuleiro.game_over_maior = True #jogo finalizado
           print(f'Jogo principal - Jogador {result} ganhou!')
        #Caso não tenha vencedores
        elif np.all(Tabuleiro.finalizados != 0): #verificar se todos os minijogos foram finalizados
            Tabuleiro.game_over_maior = True #se finalizaram, indica que o resultado é velha e o jogo também finalizou
            print(f'Jogo principal - Deu velha!')

#Classe que representa o jogo (parte gráfica)
class UltimateTicTacToe(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jogo da velha com threads")
        self.setGeometry(100, 100, 900, 600)
        self.initUI()

    #Iniciando a interface
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout() #layout horizontal para o jogo principal e minijogos

        self.grid = QGridLayout()
        self.buttons = [[QPushButton("") for _ in range(3)] for _ in range(3)] #botões para representar as posições
        
        #Matriz do jogo principal
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].setFixedSize(150, 150)
                self.buttons[i][j].setStyleSheet("font-size: 24px;")
                self.grid.addWidget(self.buttons[i][j], i, j)

        #Botão de Iniciar
        self.start_button = QPushButton("Começar Jogo")
        self.start_button.clicked.connect(self.start_games) #inicializa o jogo

        #Botão de Reiniciar
        self.reset_button = QPushButton("Reiniciar")
        self.reset_button.clicked.connect(self.restart_game) #reinicia o jogo
        self.reset_button.setEnabled(False) #só ativa após o jogo começar

        #Layout principal (à esquerda)
        left_layout = QVBoxLayout()
        left_layout.addLayout(self.grid) #jogo principal
        left_layout.addWidget(self.start_button) #botão de início
        left_layout.addWidget(self.reset_button) #botão de reinicialização

        #Matriz de minijogos
        self.mini_games_layout = QGridLayout()
        self.mini_games = [[self.create_mini_board(i * 3 + j) for j in range(3)] for i in range(3)]

        #Montagem da matriz composta pelos 9 minijogos
        for i in range(3):
            for j in range(3):
                self.mini_games_layout.addWidget(self.mini_games[i][j], i, j)

        # Layout do lado direito com os mini-jogos
        right_layout = QVBoxLayout()
        right_layout.addLayout(self.mini_games_layout)

        #Layout principal que organiza o lado esquerdo e direito
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        central_widget.setLayout(main_layout)

    #Especificações gráficas dos minijogos
    def create_mini_board(self, board_index):
        frame = QFrame()
        frame.setStyleSheet("border: 2px solid black;")
        layout = QGridLayout()
        buttons = [[QPushButton("") for _ in range(3)] for _ in range(3)]

        #Matriz de cada minijogo
        for i in range(3):
            for j in range(3):
                buttons[i][j].setFixedSize(40, 40)
                buttons[i][j].setStyleSheet("font-size: 14px;")
                layout.addWidget(buttons[i][j], i, j)
        frame.setLayout(layout)
        return frame
    
    #Atualizando a interface
    def update_ui(self, board_index, player, tamanho, x, y): #tamanho 0=pequeno, 1=grande
        row, col = divmod(board_index, 3)

        #Inserindo a jogada no tabuleiro maior
        if tamanho == 1 and player != 0:
            self.buttons[row][col].setText("X" if player == 1 else "O") #conversão de 1 e 2 para X e O

        #Atualizando os mini-jogos na lateral
        if tamanho == 0:
            mini_game_row, mini_game_col = row, col
            widget = self.mini_games[mini_game_row][mini_game_col] #obtém o QFrame do mini-tabuleiro
        
            layout = widget.layout() #obtém o layout de grade dentro do mini-tabuleiro

            btn = layout.itemAtPosition(x, y).widget()
            if btn.text() == "": #encontra um botão vazio e preenche com a jogada
                btn.setText("X" if player == 1 else "O")
                return #sai da função após marcar a jogada
        else:
            return

                
    #Para começar o jogo
    def start_games(self):
        self.start_button.setEnabled(False)  #desativa o botão de início
        self.reset_button.setEnabled(True)  #ativa o botão de reinício

        #Criar sempre novos tabuleiros ao iniciar
        self.tabuleiros = [Tabuleiro(i, self.update_ui) for i in range(9)]
        
        for t in self.tabuleiros:
            t.start()
        
        for t in self.tabuleiros:
            t.resultado()


    #Def para resetar o jogo
    def restart_game(self):
        #Reset das variáveis estáticas da classe Tabuleiro
        Tabuleiro.resultados.fill(0)
        Tabuleiro.finalizados.fill(0)
        Tabuleiro.game_over_maior = False

        #Apagar os mini-tabuleiros antigos e recriar novos
        for i in range(3):
            for j in range(3):
                #Limpa os botões principais
                self.buttons[i][j].setText("")
                
                #Limpa os mini-tabuleiros
                mini_game_widget = self.mini_games[i][j]  #obtém o QFrame
                layout = mini_game_widget.layout()  #obtém o QGridLayout do QFrame
                for x in range(3):
                    for y in range(3):
                        btn = layout.itemAtPosition(x, y).widget()
                        if btn:
                            btn.setText("")  #limpa o texto dos botões pequenos

        #Criar novos tabuleiros (descartar os antigos)
        self.tabuleiros = []

        #Habilitar e desabilitar botões
        self.start_button.setEnabled(True)  #permite iniciar um novo jogo
        self.reset_button.setEnabled(False)  #desativa o botão de reinício até novo jogo começar


if __name__ == "__main__":

    #Inicialização e funcionamento do jogo
    app = QApplication(sys.argv)
    window = UltimateTicTacToe()
    window.show()
    sys.exit(app.exec_())