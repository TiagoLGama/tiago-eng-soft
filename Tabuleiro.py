from tkinter import Canvas
from Peca import Peca
import Jogador as jogador

# 	Board matchStatus
# 1 - no match (initial state)
# 2 - finished match (game with winner - no tied game)
# 3 - your turn, match in progress AND NOT move occurring (waiting first action)
# 4 - your turn, match in progress AND move occurring (waiting second action)
# 5 - NOT your turn, match in progress - waiting move
# 6 - match abandoned by opponent

class Tabuleiro:
    def __init__(self, root, grid_size=5):
        self.jogador_local = jogador.Jogador()
        self.jogador_remoto = jogador.Jogador()
        self.jogador_local.inicializar(1, "Red player", "Red player")
        self.jogador_remoto.inicializar(2, "Blue player", "Blue player")

        self.status_partida = 1
        self.grid_size = grid_size
        self.board_margin = 50
        self.canvas_width = 500
        self.canvas_height = 500
        self.cell_size = (self.canvas_width - 2 * self.board_margin) / self.grid_size

        self.pieces = [
            Peca(0, 0, "black", "X", "totem"),
            Peca(1, 1, "black", "O", "totem"),
        ]

        self.canvas = Canvas(
            root,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#333",
            highlightthickness=0
        )
        self.canvas.pack(padx=20, pady=20)
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

    def realizar_jogada(self, x: int, y: int, color: str, symbol: str) -> dict:
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            if not any(p.x == x and p.y == y for p in self.pieces):
                peca = Peca(x, y, color, symbol, "pedra")
                self.pieces.append(peca)
                self.update_interface()
        
        return {"x": x, "y": y, "color": color, "symbol": symbol, "type": "pedra", "match_status": "next"}

    def start_match(self, players, local_id):
        playerA_name = players[0][0]
        playerA_id = players[0][1]
        playerA_order = players[0][2]
        playerB_name = players[1][0]
        playerB_id = players[1][1]
        self.jogador_local.reset()
        self.jogador_remoto.reset()
        self.jogador_local.inicializar(1, playerA_id, playerA_name)
        self.jogador_remoto.inicializar(2, playerB_id, playerB_name)
        if playerA_order == "1":
            self.jogador_local.alternar_turno()
            self.match_status = 3  #    waiting piece or origin selection (first action)
        else:
            self.jogador_remoto.alternar_turno()
            self.match_status = 5  #    waiting remote action

    def get_status_partida(self):
        return self.status_partida

    def receive_move(self, a_move):
        self.pieces.append(Peca(color= a_move["color"], symbol=a_move["symbol"], type=a_move["type"], x=a_move["x"], y=a_move["y"]))
        self.update_interface()

    def receive_withdrawal_notification(self):
        pass 

    def update_interface(self):
        # Limpa o canvas
        self.canvas.delete("all")

        # Redesenha o tabuleiro
        self.draw_board()

        # Redesenha todas as peças
        for peca in self.pieces:
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