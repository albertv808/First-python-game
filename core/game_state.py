class GameState:
    def __init__(self, player1, player2, board):
        self.player1 = player1
        self.player2 = player2
        self.board = board

        self.current_player = player1
        self.turn = 1

        self.selected_piece = None
        self.valid_moves = []
        self.valid_attacks = []

        self.acted_pieces = set()

        self.phase = "setup"
        self.winner = None

    def select_piece(self, piece):
        if not piece or piece.player != self.current_player:
            return False

        if piece in self.acted_pieces:
            return False

        self.selected_piece = piece
        self.calculate_valid_actions(piece)
        return True

    def calculate_valid_actions(self, piece):
        self.valid_moves = self.board.get_valid_moves(piece)
        self.valid_attacks = self.board.get_valid_attacks(piece, self.get_enemy())

    def get_enemy(self):
        return self.player2 if self.current_player == self.player1 else self.player1

    def move(self, x, y):
        p = self.selected_piece
        if not p:
            return False

        if (x, y) not in self.valid_moves:
            return False

        self.board.move_piece(p, x, y)

        for a in p.abilities:
            a.on_move(p, self)

        return True

    def attack(self, x, y):
        attacker = self.selected_piece
        target = self.board.get_piece(x, y)

        if not attacker or not target:
            return False

        self.board.attack(attacker, target)

        for a in attacker.abilities:
            a.on_attack(attacker, target, self)

        self.mark_acted(attacker)
        return True

    def mark_acted(self, piece):
        self.acted_pieces.add(piece)
        piece.has_acted = True
        self.selected_piece = None

    def switch_turn(self):
        self.current_player = self.get_enemy()
        self.turn += 1

        self.acted_pieces = set()

        for p in self.current_player.get_alive_pieces():
            p.has_acted = False
            p.apply_turn_start(self)

    def check_game_over(self):
        if self.player1.has_lost():
            self.winner = self.player2
            return True

        if self.player2.has_lost():
            self.winner = self.player1
            return True

        return False
