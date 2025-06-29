import tkinter as tk
from tkinter import Menu, messagebox, simpledialog, Canvas
from dog.dog_actor import DogActor
from dog.dog_interface import DogPlayerInterface
from enum import Enum, auto
from Tabuleiro import Tabuleiro
from Peca import Peca


class MatchStateEnum(Enum):
    NONE = auto()
    WAITING_REMOTE = auto()
    WAITING_INPUT = auto()
    FINISHED_BY_VICTORY_CONDITION = auto()
    FINISHED_BY_WITHDRAWAL = auto()

class JogadaFase(Enum):
    SELECIONAR_TOTEM = auto()
    MOVER_TOTEM = auto()
    ESCOLHER_SIMBOLO = auto()
    COLOCAR_PECA = auto()



class InterfaceJogador(DogPlayerInterface):
    def __init__(self):
        self.tk = tk.Tk()
        self.dog_server_interface = DogActor()
        self.menubar = Menu(self.tk)
        self.arquivo = Menu(self.menubar, tearoff=0)
        self.match_state: MatchStateEnum = None

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

        self.fase_jogada = JogadaFase.SELECIONAR_TOTEM
        self.totem_selecionado = None 
        self.simbolo_escolhido = None

        self.composicao_jogada = {}

        self.current_symbol = None
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
        if self.fase_jogada != JogadaFase.ESCOLHER_SIMBOLO:
            messagebox.showerror("Jogada inválida", "Não está na vez de selecionar uma peça")
            return

        self.simbolo_escolhido = value
        self.fase_jogada = JogadaFase.COLOCAR_PECA
        messagebox.showinfo("Simbolo selecionado", f"Simbolo {value} selecionado.")



    def on_click_event(self, event):
        x = int((event.x - self.board_margin) // self.cell_size)
        y = int((event.y - self.board_margin) // self.cell_size)

        if self.match_state != MatchStateEnum.WAITING_INPUT:
            messagebox.showerror("Jogada inválida", "Não é o seu turno!")
            return

        match self.fase_jogada:
            case JogadaFase.SELECIONAR_TOTEM:
                peca = self.tabuleiro.get_peca(x, y)
                if peca and peca.type == "totem":
                    self.totem_selecionado = peca
                    self.fase_jogada = JogadaFase.MOVER_TOTEM
                    messagebox.showinfo("Totem selecionado", f"Totem em ({x}, {y}) selecionado.")
                else:
                    messagebox.showwarning("Seleção inválida", "Selecione um Totem válido (preto).")

            case JogadaFase.MOVER_TOTEM:
                if self.tabuleiro.get_peca(x, y):
                    messagebox.showwarning("Movimento inválido", "Já existe uma peça nessa posição.")
                    return
                
                # Verifica movimento ortogonal do totem
                from_x = self.totem_selecionado.x
                from_y = self.totem_selecionado.y

                movimento_diagonal = from_x != x and from_y != y

                if movimento_diagonal:
                    ortogonal_disponivel = False

                    # Verifica todas as casas na mesma linha (x fixo) e coluna (y fixo)
                    for i in range(5):
                        if i != from_y and not self.tabuleiro.get_peca(from_x, i):
                            ortogonal_disponivel = True
                            break
                        if i != from_x and not self.tabuleiro.get_peca(i, from_y):
                            ortogonal_disponivel = True
                            break

                    if ortogonal_disponivel:
                        messagebox.showwarning("Movimento inválido", "Movimento diagonal não permitido enquanto houver casas ortogonais livres.")
                        return
                            
                self.totem_selecionado.x = x
                self.totem_selecionado.y = y
                self.composicao_jogada = {
                    "totem": {
                    "x": x,
                    "y": y,
                    "symbol": self.totem_selecionado.symbol
                    }
                }
                self.totem_selecionado = None

                self.update_interface()
                self.fase_jogada = JogadaFase.ESCOLHER_SIMBOLO
                messagebox.showinfo("Totem movido", "Agora selecione um símbolo (X ou O).")

            case JogadaFase.ESCOLHER_SIMBOLO:
                if self.simbolo_escolhido == None:
                    messagebox.showwarning("Movimento inválido", "Você deve selecionar um simbolo")
                    return
                
            case JogadaFase.COLOCAR_PECA:
                if self.simbolo_escolhido is None:
                    messagebox.showwarning("Símbolo não escolhido", "Você precisa escolher X ou O antes.")
                    return
                if self.tabuleiro.get_peca(x, y):
                    messagebox.showwarning("Posição ocupada", "Essa posição já está ocupada.")
                    return

                totem_x = self.composicao_jogada["totem"]["x"]
                totem_y = self.composicao_jogada["totem"]["y"]

                adjacentes_vazias = self.get_posicoes_adjacentes_vazias(totem_x, totem_y)

                if adjacentes_vazias:
                    if (x, y) not in adjacentes_vazias:
                        messagebox.showwarning(
                            "Movimento inválido",
                            "Você só pode colocar a peça em uma célula adjacente vazia ao Totem movido."
                        )
                        return

                nova_peca = self.tabuleiro.realizar_jogada(x, y, self.current_color, self.simbolo_escolhido)

                condicao_vitoria_atingida = self.verificar_vitoria(x, y, self.current_color, self.simbolo_escolhido)

                match_status = "next"
                if condicao_vitoria_atingida:
                    match_status = "finished"
                    messagebox.showwarning("Partida finalizada", "você venceu!")
                    self.match_state = MatchStateEnum.FINISHED_BY_VICTORY_CONDITION
                else:
                    self.match_state = MatchStateEnum.WAITING_REMOTE
                    self.fase_jogada = JogadaFase.SELECIONAR_TOTEM
                    self.simbolo_escolhido = None

                self.composicao_jogada["peca"] = nova_peca
                self.composicao_jogada["match_status"] = match_status
            
                self.update_interface()
                self.dog_server_interface.send_move(self.composicao_jogada)
                


    def start_match(self):
        self.current_color = "blue"
        self.current_symbol = "X"
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
                    self.match_state = MatchStateEnum.WAITING_INPUT
                    messagebox.showinfo(message=start_status.get_message())

    def receive_start(self, start_status):
        self.current_color = "red"
        self.current_symbol = "O"
        self.atualizar_cor_botoes(self.current_color)

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
        self.game_state = self.tabuleiro.get_status_partida()
        self.match_state = MatchStateEnum.FINISHED_BY_WITHDRAWAL
        messagebox.showinfo("Vitória por desistência", "Adversário abandonou a partida!")

    def receive_move(self, a_move: dict):
        self.tabuleiro.receive_move(a_move)
        if a_move["match_status"] == "finished":
            self.match_state = MatchStateEnum.FINISHED_BY_VICTORY_CONDITION
            messagebox.showinfo("Partida Finalizada", "Você foi derrotado!")
        else :
            self.game_state = self.tabuleiro.get_status_partida()
            self.match_state = MatchStateEnum.WAITING_INPUT
        
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

    def get_posicoes_adjacentes_vazias(self, x: int, y: int):
        adjacentes = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if dx == 0 and dy == 0:
                    continue
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    if not self.tabuleiro.get_peca(nx, ny):
                        adjacentes.append((nx, ny))
        return adjacentes

    def verificar_vitoria(self, x, y, cor, simbolo):
        direcoes = [
            (1, 0),  
            (0, 1),  
            (1, 1),  
            (1, -1), 
        ]

        for dx, dy in direcoes:
            cont_cor = 1
            cont_simbolo = 1

            for sentido in [-1, 1]:
                nx, ny = x, y
                while True:
                    nx += dx * sentido
                    ny += dy * sentido
                    if 0 <= nx < 5 and 0 <= ny < 5:
                        peca = self.tabuleiro.get_peca(nx, ny)
                        if not peca or peca.type == "totem":
                            break

                        if peca.color == cor:
                            cont_cor += 1
                        if peca.symbol == simbolo:
                            cont_simbolo += 1
                    else:
                        break

            if cont_cor >= 4 or cont_simbolo >= 4:
                return True

        return False
