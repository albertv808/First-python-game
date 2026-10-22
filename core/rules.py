class Rules:

    @staticmethod
    def get_valid_moves(board, piece):
        """Retorna les caselles accessibles per la peça."""

        if piece is None or not piece.is_alive:
            return []

        return board.get_valid_moves(piece)

    @staticmethod
    def get_valid_attacks(board, piece, enemy_player):
        """Retorna les posicions enemigues dins del rang d'atac."""

        if piece is None or not piece.is_alive:
            return []

        if piece.troop.attack_range <= 0:
            return []

        return board.get_valid_attacks(piece, enemy_player)

    @staticmethod
    def can_move(board, piece, x, y):
        return (x, y) in Rules.get_valid_moves(board, piece)

    @staticmethod
    def can_attack(board, piece, x, y, enemy_player):
        return (x, y) in Rules.get_valid_attacks(
            board, piece, enemy_player
        )