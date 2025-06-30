import tkinter as tk
from tkinter import Menu, messagebox, simpledialog, Canvas
from dog.dog_actor import DogActor
from dog.dog_interface import DogPlayerInterface
from Tabuleiro import Tabuleiro, JogadaFase, MatchStateEnum
from Peca import Peca



class InterfaceJogador(DogPlayerInterface):
    def __init__(self):
        self.tk = tk.Tk()
        self.dog_server_interface = DogActor()
        self.menubar = Menu(self.tk)
        self.arquivo = Menu(self.menubar, tearoff=0)

        self.canvas_width = 500
        self.canvas_height = 500
        self.canvas = Canvas(
            self.tk,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#333",
            highlightthickness=0
        ) 
        self.grid_size = 5
        self.board_margin = 50
        
        self.canvas.pack(padx=20, pady=20)
        self.cell_size = (self.canvas_width - 2 * self.board_margin) / self.grid_size

        self.tabuleiro = Tabuleiro(self.grid_size)

        self.composicao_jogada = {}

        self.current_color = None

        self.update_interface()

        self.arquivo.add_command(label="Iniciar jogo", command=self.start_match)
        self.arquivo.add_command(label="Restaurar estado inicial", command=self.start_game)
        self.arquivo.add_command(label="desistir", command=self.start_game)
        
        self.menubar.add_cascade(label="Arquivo", menu=self.arquivo)
        self.tk.config(menu=self.menubar)

        self.canvas.bind("<Button-1>", self.on_click_event)

        # Frame para exibir as peças
        self.controls_frame = tk.Frame(self.tk, bg="#333")
        self.controls_frame.pack(pady=(0, 20))

        self.botao_x = tk.Button(
            self.controls_frame,
            text="X",
            bg="gray",
            fg="white",
            font=("Arial", 16, "bold"),
            width=4,
            height=2,
            command=lambda: self.selecionar_simbolo("X")
        )
        self.botao_x.pack(side=tk.LEFT, padx=10)

        self.botao_o = tk.Button(
            self.controls_frame,
            text="O",
            bg="gray",
            fg="white",
            font=("Arial", 16, "bold"),
            width=4,
            height=2,
            command=lambda: self.selecionar_simbolo("O")
        )
        self.botao_o.pack(side=tk.LEFT, padx=10)

        nome_jogador = simpledialog.askstring("Nome do Jogador", "Digite seu nome:")
        mensagem = self.dog_server_interface.initialize(nome_jogador, self)
        messagebox.showinfo(message=mensagem)

    def selecionar_simbolo(self, value: str):
        if self.tabuleiro.fase_jogada != JogadaFase.ESCOLHER_SIMBOLO:
            messagebox.showerror("Jogada inválida", "Não está na vez de selecionar uma peça")
            return

        self.tabuleiro.simbolo_escolhido = value
        self.tabuleiro.fase_jogada = JogadaFase.COLOCAR_PECA
        messagebox.showinfo("Simbolo selecionado", f"Simbolo {value} selecionado.")


    def on_click_event(self, event):
        x = int((event.x - self.board_margin) // self.cell_size)
        y = int((event.y - self.board_margin) // self.cell_size)

        self.composicao_jogada = self.tabuleiro.realizar_jogada(x, y, self.current_color)
        self.update_interface()
        if self.composicao_jogada != None:
            self.dog_server_interface.send_move(self.composicao_jogada)
                

    def start_match(self):
        self.current_color = "blue"
        self.atualizar_cor_botoes(self.current_color)

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
                    self.tabuleiro.jogador_local.alternar_turno()
                    self.tabuleiro.match_state = MatchStateEnum.WAITING_INPUT
                    messagebox.showinfo(message=start_status.get_message())

    def receive_start(self, start_status):
        self.current_color = "red"
        self.atualizar_cor_botoes(self.current_color)

        self.start_game()
        players = start_status.get_players()
        local_player_id = start_status.get_local_id()
        self.tabuleiro.start_match(players, local_player_id)
        self.game_state = self.tabuleiro.get_status_partida()
        self.tabuleiro.match_state = MatchStateEnum.WAITING_REMOTE
        messagebox.showinfo(message="Recebe início partida")

    def start_game(self):
        match_status = self.tabuleiro.get_status_partida()
        if match_status == 2 or match_status == 6:
            self.tabuleiro.reset_game()
            self.game_state = self.tabuleiro.get_status_partida()

    def receive_withdrawal_notification(self):
        self.game_state = self.tabuleiro.get_status_partida()
        self.tabuleiro.match_state = MatchStateEnum.FINISHED_BY_WITHDRAWAL
        messagebox.showinfo("Vitória por desistência", "Adversário abandonou a partida!")

    def receive_move(self, a_move: dict):
        self.tabuleiro.receive_move(a_move)
        if a_move["match_status"] == "finished":
            self.tabuleiro.match_state = MatchStateEnum.FINISHED_BY_VICTORY_CONDITION
            messagebox.showinfo("Partida Finalizada", "Você foi derrotado!")
        else :
            self.game_state = self.tabuleiro.get_status_partida()
            self.tabuleiro.match_state = MatchStateEnum.WAITING_INPUT
        
        self.update_interface()


    def draw_board(self):
        board_size = self.canvas_width - (2 * self.board_margin)
        self.canvas.create_rectangle(
            self.board_margin, self.board_margin,
            self.board_margin + board_size, self.board_margin + board_size,
            fill="#663399", outline="white", width=2
        )
        for i in range(1, self.grid_size):
            self.canvas.create_line(
                self.board_margin, self.board_margin + i * self.cell_size,
                self.board_margin + board_size, self.board_margin + i * self.cell_size,
                fill="white"
            )
            self.canvas.create_line(
                self.board_margin + i * self.cell_size, self.board_margin,
                self.board_margin + i * self.cell_size, self.board_margin + board_size,
                fill="white"
            )

    def update_interface(self):
        self.canvas.delete("all")
        self.draw_board()
        for peca in self.tabuleiro.pieces:
            self._desenhar_peca(peca)
    
    def _desenhar_peca(self, peca: Peca):
        x, y = peca.x, peca.y
        self.canvas.create_oval(
            self.board_margin + x * self.cell_size + 5,
            self.board_margin + y * self.cell_size + 5,
            self.board_margin + (x + 1) * self.cell_size - 5,
            self.board_margin + (y + 1) * self.cell_size - 5,
            fill=peca.color,
            outline="black"
        )
        self.canvas.create_text(
            self.board_margin + (x + 0.5) * self.cell_size,
            self.board_margin + (y + 0.5) * self.cell_size,
            text=peca.symbol,
            fill="white",
            font=("Arial", 16, "bold")
        )

    def executar(self):
        self.tk.title("Oxono multiplayer")
        self.tk.configure(bg="#333")
        self.tk.mainloop()

    def atualizar_cor_botoes(self, cor):
        self.botao_x.config(bg=cor)
        self.botao_o.config(bg=cor)
