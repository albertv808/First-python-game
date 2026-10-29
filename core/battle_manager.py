from core.rules import Rules


class BattleManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.board = game_state.board

        self.players = [
            game_state.player1,
            game_state.player2
        ]

        self.current_player_index = 0
        self.current_player = self.players[0]

        self.selected_piece = None

        self.moved_pieces = set()
        self.attacked_pieces = set()

        self.winner = None

        self.game_state.current_player = self.current_player
        self.game_state.phase = "battle"
        self.last_combat_log = None

    def get_enemy_player(self):
        return self.players[1 - self.current_player_index]

    def get_player_pieces(self, player):
        return [
            piece
            for row in self.board.grid
            for piece in row
            if (
                piece is not None
                and piece.is_alive
                and piece.player == player
            )
        ]

    def select_piece(self, piece):
        if piece is None or not piece.is_alive:
            return False

        if piece.player != self.current_player:
            return False

        if piece.has_acted:
            return False

        self.selected_piece = piece

        for ability in piece.abilities:
            ability.on_select(piece, self.game_state)

        return True

    def get_valid_moves(self):
        piece = self.selected_piece

        if piece is None:
            return []

        if piece.has_acted:
            return []

        # Només es pot moure una vegada i abans d'atacar.
        if piece in self.moved_pieces:
            return []

        if piece in self.attacked_pieces:
            return []

        return Rules.get_valid_moves(self.board, piece)

    def get_valid_attacks(self):
        piece = self.selected_piece

        if piece is None:
            return []

        if piece.has_acted:
            return []

        if piece in self.attacked_pieces:
            return []

        return Rules.get_valid_attacks(
            self.board,
            piece,
            self.get_enemy_player()
        )

    def move_selected_piece(self, x, y):
        piece = self.selected_piece

        if piece is None:
            return False

        if (x, y) not in self.get_valid_moves():
            return False

        if not self.board.move_piece(piece, x, y):
            return False

        self.moved_pieces.add(piece)

        for ability in piece.abilities:
            ability.on_move(piece, self.game_state)

        # La peça continua seleccionada.
        # Els atacs es calcularan des de la nova posició.
        return True

    def attack_selected_piece(self, x, y):
        attacker = self.selected_piece

        if attacker is None:
            return False

        if (x, y) not in self.get_valid_attacks():
            return False

        target = self.board.get_piece(x, y)

        if target is None:
            return False

        if target.player == self.current_player:
            return False

        # Executar l'atac i aplicar el dany.
        damage = self.board.attack(attacker, target)

        # Recuperar el registre detallat del combat.
        self.last_combat_log = getattr(self.board, "last_combat_log", None)

        if damage <= 0:
            return False

        self.attacked_pieces.add(attacker)

        # Activar les habilitats de l'atacant.
        for ability in attacker.abilities:
            ability.on_attack(attacker, target, self.game_state)

        # Comprovar si la batalla ha acabat.
        self.check_victory()

        return True

    def finish_piece_action(self):
        piece = self.selected_piece

        if piece is None:
            return False

        for ability in piece.abilities:
            ability.on_turn_end(piece, self.game_state)

        piece.has_acted = True
        self.selected_piece = None
        self.last_combat_log = None

        self.check_victory()

        if self.winner is not None:
            return True

        if self.all_pieces_acted():
            self.next_turn()

        return True

    def all_pieces_acted(self):
        pieces = self.get_player_pieces(self.current_player)

        return all(piece.has_acted for piece in pieces)

    def next_turn(self):
        self.check_victory()

        if self.winner is not None:
            return

        self.current_player_index = 1 - self.current_player_index
        self.current_player = self.players[
            self.current_player_index
        ]

        self.game_state.current_player = self.current_player
        self.game_state.turn += 1

        self.moved_pieces.clear()
        self.attacked_pieces.clear()
        self.selected_piece = None

        for piece in self.get_player_pieces(self.current_player):
            piece.has_acted = False

            for ability in piece.abilities:
                ability.on_turn_start(piece, self.game_state)

    def check_victory(self):
        alive1 = self.get_player_pieces(self.players[0])
        alive2 = self.get_player_pieces(self.players[1])

        if not alive1:
            self.winner = self.players[1]
        elif not alive2:
            self.winner = self.players[0]

        if self.winner is not None:
            self.game_state.winner = self.winner
            self.game_state.phase = "final"
            self.selected_piece = None
            return True

        return False
