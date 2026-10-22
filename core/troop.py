from data.troops_data import TROOPS


class Troop:
    def __init__(self, troop_key):
        data = TROOPS[troop_key]

        self.key = troop_key
        self.name = data["name"]
        self.symbol = data["symbol"]

        # economia
        self.cost = data["cost"]

        # stats base
        self.life = data["life"]
        self.attack = data["attack"]
        self.defence = data["defence"]
        self.damage = data["damage"]
        self.movement = data["movement"]
        self.attack_range = data["attack_range"]

        # habilitats (només noms aquí)
        self.abilities = data["abilities"]
