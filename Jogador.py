class Jogador:
    def __init__(self):
        self.identificado = ""  #   string
        self.nome = ""  #   string
        self.codinome = None  # int
        self.turno = False  # bool
        self.ganhador = False  # bool
        self.selected_piece = 0  # int: 0 - no piece; 1 - small, 2 - medium, 3 - large

    def inicializar(self, codinome, id, nome):  # Name!!!!
        self.reset()
        self.id = id  #   string
        self.codinome = codinome  # int
        self.nome = nome  #   string

    def alternar_turno(self):
        if self.turno == False:
            self.turno = True
        elif self.turno == True:
            self.turno = False

    def reset(self):
        self.identificador = ""  #   string
        self.nome = ""  #   string
        self.codinome = None  # int
        self.turno = False  # bool
        self.ganhador = False  # bool
        self.selected_piece = 0  # int: 0 - no piece; 1 - small, 2 - medium, 3 - large

