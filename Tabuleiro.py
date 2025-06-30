from typing import Optional
from tkinter import messagebox
from enum import Enum, auto
from Peca import Peca
import Jogador as jogador

# 	Board matchStatus
# 1 - no match (initial state)
# 2 - finished match (game with winner - no tied game)
# 3 - your turn, match in progress AND NOT move occurring (waiting first action)
# 4 - your turn, match in progress AND move occurring (waiting second action)
# 5 - NOT your turn, match in progress - waiting move
# 6 - match abandoned by opponent

class MatchStateEnum(Enum):
    NONE = auto()
    WAITING_REMOTE = auto()
    WAITING_INPUT = auto()
    FINISHED_BY_VICTORY_CONDITION = auto()
    FINISHED_BY_WITHDRAWAL = auto()
    FINISHED_IN_A_DRAW = auto()

class JogadaFase(Enum):
    SELECIONAR_TOTEM = auto()
    MOVER_TOTEM = auto()
    ESCOLHER_SIMBOLO = auto()
    COLOCAR_PECA = auto()

class Tabuleiro:
    def __init__(self, grid_size = 5):
        self.jogador_local = jogador.Jogador()
        self.jogador_remoto = jogador.Jogador()
        self.jogador_local.inicializar(1, "Red player", "Red player")
        self.jogador_remoto.inicializar(2, "Blue player", "Blue player")
        self.grid_size = grid_size
        self.match_state = None
        self.fase_jogada = JogadaFase.SELECIONAR_TOTEM
        
        self.totem_selecionado = None
        self.simbolo_escolhido = None

        self.status_partida = 1
    
    
        self.pieces = [
            Peca(0, 0, "black", "X", "totem"),
            Peca(1, 1, "black", "O", "totem"),
        ]

    def realizar_jogada(self, x, y, color) -> dict:
        if self.match_state != MatchStateEnum.WAITING_INPUT:
            messagebox.showerror("Jogada inválida", "Não é o seu turno!")
            return

        match self.fase_jogada:
            case JogadaFase.SELECIONAR_TOTEM:
                peca = self.get_peca(x, y)
                if peca and peca.type == "totem":
                    self.totem_selecionado = peca
                    self.fase_jogada = JogadaFase.MOVER_TOTEM
                    messagebox.showinfo("Totem selecionado", f"Totem em ({x}, {y}) selecionado.")
                else:
                    messagebox.showwarning("Seleção inválida", "Selecione um Totem válido (preto).")

            case JogadaFase.MOVER_TOTEM:
                if self.get_peca(x, y):
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
                        if i != from_y and not self.get_peca(from_x, i):
                            ortogonal_disponivel = True
                            break
                        if i != from_x and not self.get_peca(i, from_y):
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
                if self.get_peca(x, y):
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

                nova_peca = self.adicionar_nova_peca(x, y, color, self.simbolo_escolhido)

                condicao_vitoria_atingida = self.verificar_vitoria(x, y, color, self.simbolo_escolhido)
                condicao_empate_atingida = self.tabuleiro_cheio()
                
                match_status = "next"
                
                if condicao_vitoria_atingida:
                    match_status = "finished"
                    messagebox.showwarning("Partida finalizada", "você venceu!")
                    self.match_state = MatchStateEnum.FINISHED_BY_VICTORY_CONDITION
                elif condicao_empate_atingida:
                    match_status = "finished"
                    messagebox.showwarning("Partida finalizada", "O jogo empatou")
                    self.match_state = MatchStateEnum.FINISHED_IN_A_DRAW
                else:
                    self.match_state = MatchStateEnum.WAITING_REMOTE
                    self.fase_jogada = JogadaFase.SELECIONAR_TOTEM
                    self.simbolo_escolhido = None

                self.composicao_jogada["peca"] = nova_peca
                self.composicao_jogada["match_status"] = match_status
                
                return self.composicao_jogada

    def adicionar_nova_peca(self, x: int, y: int, color: str, symbol: str) -> dict:
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            if not any(p.x == x and p.y == y for p in self.pieces):
                peca = Peca(x, y, color, symbol, "pedra")
                self.pieces.append(peca)
        
        return {"x": x, "y": y, "color": color, "symbol": symbol}

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
        peca_move = a_move["peca"]
        totem_move = a_move["totem"]

        # Adiciona a nova peça
        self.pieces.append(Peca(
            color=peca_move["color"],
            symbol=peca_move["symbol"],
            type="peca",
            x=peca_move["x"],
            y=peca_move["y"]
        ))

        # Atualiza a posição do totem existente
        for peca in self.pieces:
            if peca.type == "totem" and peca.symbol == totem_move["symbol"]:
                peca.x = totem_move["x"]
                peca.y = totem_move["y"]
                self.totem = peca
                return                 
    

    def get_peca(self, x: int, y: int) -> Optional[Peca]:
        for peca in self.pieces:
            if peca.x == x and peca.y == y:
                return peca
        return None
    
    def get_posicoes_adjacentes_vazias(self, x: int, y: int):
        adjacentes = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if dx == 0 and dy == 0:
                    continue
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    if not self.get_peca(nx, ny):
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
                        peca = self.get_peca(nx, ny)
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
    
    def tabuleiro_cheio(self) -> bool:
        return len(self.pieces) >= self.grid_size * self.grid_size
