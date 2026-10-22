class Ability:
    def on_select(self, piece, game_state):
        pass
    def on_move(self, piece, game_state):
        pass
    def on_attack(self, attacker, defender, game_state):
        pass
    def on_turn_start(self, piece, game_state):
        pass
    def on_turn_end(self, piece, game_state):
        pass

ABILITY_REGISTRY = {
}

def create_ability(name):
    cls = ABILITY_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Ability '{name}' no existeix")
    return cls()

