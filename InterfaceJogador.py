import tkinter as tk
from tkinter import Menu, messagebox, simpledialog
from dog.dog_actor import DogActor
from dog.dog_interface import DogPlayerInterface
from enum import Enum, auto
from Tabuleiro import Tabuleiro


class MatchStateEnum(Enum):
    NONE = auto()
    WAITING_REMOTE = auto()
    WAITING_INPUT = auto()
    FINISHED_BY_VICTORY = auto()


class InterfaceJogador(DogPlayerInterface):
    def __init__(self):
        self.tk = tk.Tk()
        self.tabuleiro = Tabuleiro(self.tk)
        self.dog_server_interface = DogActor()
        self.menubar = Menu(self.tk)
        self.arquivo = Menu(self.menubar, tearoff=0)
        self.match_state: MatchStateEnum = None

        self.arquivo.add_command(label="Iniciar jogo", command=self.start_match)
        self.arquivo.add_command(
            label="Restaurar estado inicial", command=self.start_game
        )
        self.menubar.add_cascade(label="Arquivo", menu=self.arquivo)
        self.tk.config(menu=self.menubar)

        self.tabuleiro.canvas.bind("<Button-1>", self.on_click_event)

        nome_jogador = simpledialog.askstring("Nome do Jogador", "Digite seu nome:")
        mensagem = self.dog_server_interface.initialize(nome_jogador, self)
        messagebox.showinfo(message=mensagem)

        self.current_symbol = "X"
        self.current_color = "#cc0000"

    def on_click_event(self, event):
        print(self.tabuleiro.jogador_local.turno)

        if self.match_state != MatchStateEnum.WAITING_INPUT:
            messagebox.showerror("Jogada inválida", "Não é o seu turno!")
            return

        x = int((event.x - self.tabuleiro.board_margin) // self.tabuleiro.cell_size)
        y = int((event.y - self.tabuleiro.board_margin) // self.tabuleiro.cell_size)

        move_pieces = self.tabuleiro.realizar_jogada(
            x, y, self.current_color, self.current_symbol
        )
        self.toggle_player()
        print("passou no send_move")
        self.dog_server_interface.send_move(move_pieces)
        self.match_state = MatchStateEnum.WAITING_REMOTE

    def toggle_player(self):
        if self.current_symbol == "X":
            self.current_symbol = "O"
            self.current_color = "blue"
        else:
            self.current_symbol = "X"
            self.current_color = "#cc0000"

    def start_match(self):
        match_status = self.tabuleiro.get_status_partida()
        if match_status == 1:
            answer = messagebox.askyesno("START", "Deseja iniciar uma nova partida?")
            if answer:
                start_status = self.dog_server_interface.start_match(2)
                code = start_status.get_code()
                message = start_status.get_message()
                if code == "0" or code == "1":
                    messagebox.showinfo(message=message)
                else:
                    players = start_status.get_players()
                    local_player_id = start_status.get_local_id()
                    self.tabuleiro.start_match(players, local_player_id)
                    self.tabuleiro.jogador_local.alternar_turno()  # dá o turno a ele
                    self.match_state = MatchStateEnum.WAITING_INPUT
                    messagebox.showinfo(message=start_status.get_message())

    def receive_start(self, start_status):
        self.start_game()
        players = start_status.get_players()
        local_player_id = start_status.get_local_id()
        self.tabuleiro.start_match(players, local_player_id)
        self.game_state = self.tabuleiro.get_status_partida()
        self.match_state = MatchStateEnum.WAITING_REMOTE
        messagebox.showinfo(message="Recebe início partida")

    def start_game(self):
        match_status = self.tabuleiro.get_status_partida()
        if match_status == 2 or match_status == 6:
            self.tabuleiro.reset_game()
            self.game_state = self.tabuleiro.get_status_partida()

    def receive_withdrawal_notification(self):
        self.tabuleiro.receive_withdrawal_notification()
        self.game_state = self.tabuleiro.get_status_partida()

    def receive_move(self, a_move: dict):
        print("recebido")
        print(a_move)
        self.tabuleiro.receive_move(a_move)
        self.game_state = self.tabuleiro.get_status_partida()
        self.match_state = MatchStateEnum.WAITING_INPUT

    def executar(self):
        self.tk.title("Oxono multiplayer")
        self.tk.configure(bg="#333")
        self.tk.mainloop()
