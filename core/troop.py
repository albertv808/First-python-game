from data.troops_data import TROOPS


class Troop:
    """Defineix les estadístiques base i l'equipament d'una tropa."""

    def __init__(self, troop_key):
        if troop_key not in TROOPS:
            raise KeyError(
                f"No existeix la definició de tropa '{troop_key}'."
            )

        data = TROOPS[troop_key]

        self.key = troop_key
        self.name = data["name"]
        self.symbol = data["symbol"]

        # Economia.
        self.cost = data["cost"]

        # Estadístiques base.
        self.life = data["life"]
        self.attack = data["attack"]
        self.defence = data["defence"]
        self.damage = data["damage"]
        self.movement = data["movement"]
        self.attack_range = data["attack_range"]

        # Tipus d'atac: melee o ranged.
        # Per defecte, les tropes antigues són cos a cos.
        self.attack_type = data.get("attack_type", "melee")

        if self.attack_type not in ("melee", "ranged"):
            raise ValueError(
                f"Tipus d'atac no vàlid per a '{troop_key}': "
                f"{self.attack_type}"
            )

        # Tipus i modificador del dany de l'arma.
        self.damage_type = data["damage_type"]
        self.damage_modifier = data["damage_modifier"]

        # Armadura.
        self.armor_type = data["armor_type"]
        self.armor_modifier = data["armor_modifier"]

        # Escut.
        self.shield_type = data["shield_type"]
        self.shield_modifier = data["shield_modifier"]

        # Habilitats.
        self.abilities = list(data["abilities"])