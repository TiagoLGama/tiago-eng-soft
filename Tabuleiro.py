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
    def __init__(self, grid_size = 5):
        self.jogador_local = jogador.Jogador()
        self.jogador_remoto = jogador.Jogador()
        self.jogador_local.inicializar(1, "Red player", "Red player")
        self.jogador_remoto.inicializar(2, "Blue player", "Blue player")
        self.grid_size = grid_size

        self.status_partida = 1

        self.pieces = [
            Peca(0, 0, "black", "X", "totem"),
            Peca(1, 1, "black", "O", "totem"),
        ]

    def realizar_jogada(self, x: int, y: int, color: str, symbol: str) -> dict:
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            if not any(p.x == x and p.y == y for p in self.pieces):
                peca = Peca(x, y, color, symbol, "pedra")
                self.pieces.append(peca)
        
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

    def receive_withdrawal_notification(self):
        pass 
