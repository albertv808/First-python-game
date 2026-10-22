from core.piece import Piece


class Player:
    def __init__(self, player_id, name, money):
        self.id = player_id
        self.name = name
        self.money = money

        self.army_selection = {}
        self.pieces = []

    def can_afford(self, troop, qty):
        return self.money >= troop.cost * qty

    def spend_money(self, troop, qty):
        cost = troop.cost * qty
        if self.money < cost:
            return False
        self.money -= cost
        return True

    def add_to_army(self, troop, qty):
        if not self.can_afford(troop, qty):
            return False

        self.spend_money(troop, qty)
        self.army_selection[troop.key] = self.army_selection.get(troop.key, 0) + qty
        return True

    def deploy_piece(self, troop, count, x, y):
        piece = Piece(troop, self, x, y, count)
        self.pieces.append(piece)
        return piece

    def get_alive_pieces(self):
        return [p for p in self.pieces if p.is_alive]

    def has_lost(self):
        return not any(p.is_alive for p in self.pieces)

    def reset(self, money):
        self.money = money
        self.army_selection = {}
        self.pieces = []
