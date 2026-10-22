from core.abilities import create_ability


class Piece:
    def __init__(self, troop, player, x, y, count=1):
        self.troop = troop
        self.player = player

        # 📦 tropes completes
        self.count = count

        # ❤️ vida de la tropa actual (la "frontal")
        self.hp = troop.life

        # 📍 posició
        self.x = x
        self.y = y

        # 🎮 estat
        self.has_acted = False
        self.is_alive = True

        # ✨ efectes
        self.effects = []
        self.abilities = [create_ability(a) for a in troop.abilities]

    def _get_modifier(self, stat):
        """Suma els modificadors de les estadístiques de la peça."""
        total = 0

        for effect in self.effects:
            if isinstance(effect, dict):
                total += effect.get(stat, 0)

        return total

    def get_damage(self):
        """
        ✔ escala amb el nombre de unitats
        ✔ cada unitat aporta el seu damage base
        """
        base = self.troop.damage * self.count
        return max(0, base + self._get_modifier("damage"))

    def get_attack(self):
        """
        ✔ cada unitat NO fa més forta la unitat
        ✔ és atribut fix de la tropa
        """
        return max(0, self.troop.attack + self._get_modifier("attack"))

    def get_defence(self):
        """
        ✔ defensa també és per unitat individual
        ✔ NO depèn del count
        """
        return max(0, self.troop.defence + self._get_modifier("defence"))

    def resolve_attack(self, target):
        # 💥 dany total de la unitat atacant
        damage = self.get_damage()

        # 🛡 defensa del defensor
        defence = target.get_defence()

        # ⚔️ dany final
        final_damage = max(0, damage - defence)

        target.take_damage(final_damage)

    def take_damage(self, damage, board=None):
        if damage <= 0:
            return

        while damage > 0 and self.count > 0:
            # 💥 dany a la tropa actual
            if damage >= self.hp:
                damage -= self.hp

                # ☠️ mor una tropa
                self.count -= 1

                if self.count > 0:
                    self.hp = self.troop.life
                else:
                    self.hp = 0
                    self.is_alive = False

                    if board:
                        board.grid[self.y][self.x] = None
                    return
            else:
                # 🩸 queda danyada però viva
                self.hp -= damage
                damage = 0
