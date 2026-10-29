import json
from math import floor
from pathlib import Path


COMBAT_TYPES_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "combat_types.json"
)


def _load_combat_types():
    """Carrega les regles de combat del JSON."""
    try:
        with COMBAT_TYPES_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(
            f"No s'han pogut carregar les dades de combat: "
            f"{COMBAT_TYPES_PATH}"
        ) from error


COMBAT_TYPES = _load_combat_types()


def _get_value(unit, key, default=None):
    """Obté una propietat de Piece o de Troop."""
    if unit is None:
        return default

    # En el teu projecte, les dades base són a piece.troop.
    troop = getattr(unit, "troop", None)

    value = getattr(unit, key, None)
    if value is not None:
        return value

    value = getattr(troop, key, None)
    if value is not None:
        return value

    return default


def _get_stat(unit, method_name, attribute_name, default=0):
    """Utilitza el getter de Piece quan existeix."""
    method = getattr(unit, method_name, None)

    if callable(method):
        return method()

    return _get_value(unit, attribute_name, default)


def _is_alive(unit):
    """Comprova si la peça està viva."""
    if unit is None:
        return False

    return bool(getattr(unit, "is_alive", False))


def _get_modifier(name, modifiers, default=1.0):
    """Retorna un modificador numèric."""
    return modifiers.get(name, default)


def calculate_damage_details(attacker, target):
    """
    Calcula el dany i retorna tots els detalls del combat.

    Les resistències de l'armadura i l'escut s'apliquen
    successivament. Un atac vàlid causa almenys 1 punt de dany.
    """
    result = {
        "valid": False,
        "base_damage": 0,
        "weapon_modifier": 1.0,
        "attack": 0,
        "defence": 0,
        "defence_modifier": 1.0,
        "damage_type": None,
        "attack_type": None,
        "attack_type_modifier": 1.0,
        "armor_type": None,
        "armor_modifier": 1.0,
        "armor_resistance": 0.0,
        "shield_type": None,
        "shield_modifier": 1.0,
        "shield_resistance": 0.0,
        "damage_before_rounding": 0.0,
        "final_damage": 0,
    }

    # Validacions.
    if attacker is None or target is None:
        return result

    if not _is_alive(attacker) or not _is_alive(target):
        return result

    if attacker is target:
        return result

    # Estadístiques de les peces.
    base_damage = max(
        0,
        _get_stat(attacker, "get_damage", "damage", 0)
    )

    attack = _get_stat(attacker, "get_attack", "attack", 0)
    defence = _get_stat(target, "get_defence", "defence", 0)

    damage_type = _get_value(
        attacker, "damage_type", "blunt"
    )
    damage_modifier_name = _get_value(
        attacker, "damage_modifier", "medium"
    )

    attack_type = _get_value(
        attacker, "attack_type", "melee"
    )

    armor_type = _get_value(
        target, "armor_type", "unarmored"
    )
    armor_modifier_name = _get_value(
        target, "armor_modifier", None
    )

    shield_type = _get_value(
        target, "shield_type", "no_shield"
    )
    shield_modifier_name = _get_value(
        target, "shield_modifier", None
    )

    # Modificador del dany de l'arma.
    weapon_modifier = _get_modifier(
        damage_modifier_name,
        COMBAT_TYPES.get("damage_modifiers", {}),
    )

    # Si la defensa supera l'atac, el dany baixa un 25%.
    defence_modifier = 0.75 if attack < defence else 1.0

    # Resistència base de l'armadura segons el tipus de dany.
    armor_table = COMBAT_TYPES.get("armor", {})
    armor_data = armor_table.get(
        armor_type,
        armor_table.get("unarmored", {}),
    )

    armor_resistance = armor_data.get(damage_type, 0.0)

    # Modificador de qualitat de l'armadura.
    armor_modifier = _get_modifier(
        armor_modifier_name,
        COMBAT_TYPES.get("armor_modifiers", {}),
    )

    armor_resistance = min(
        0.95,
        max(0.0, armor_resistance * armor_modifier),
    )

    # Modificador específic per al tipus d'atac.
    attack_type_modifier = _get_modifier(
        attack_type,
        COMBAT_TYPES.get("attack_type_modifiers", {}),
    )

    # Resistència de l'escut contra melee o ranged.
    shields = COMBAT_TYPES.get("shields", {})
    shield_data = shields.get(
        shield_type,
        shields.get("no_shield", {}),
    )

    shield_resistance = shield_data.get(attack_type, 0.0)

    shield_modifier = _get_modifier(
        shield_modifier_name,
        COMBAT_TYPES.get("shield_modifiers", {}),
    )

    shield_resistance = min(
        0.95,
        max(0.0, shield_resistance * shield_modifier),
    )

    # Dany final abans d'arrodonir.
    damage = (
        base_damage
        * weapon_modifier
        * defence_modifier
        * attack_type_modifier
        * (1.0 - armor_resistance)
        * (1.0 - shield_resistance)
    )

    final_damage = max(1, floor(damage + 0.5))

    result.update({
        "valid": True,
        "base_damage": base_damage,
        "weapon_modifier": weapon_modifier,
        "attack": attack,
        "defence": defence,
        "defence_modifier": defence_modifier,
        "damage_type": damage_type,
        "attack_type": attack_type,
        "attack_type_modifier": attack_type_modifier,
        "armor_type": armor_type,
        "armor_modifier": armor_modifier,
        "armor_resistance": armor_resistance,
        "shield_type": shield_type,
        "shield_modifier": shield_modifier,
        "shield_resistance": shield_resistance,
        "damage_before_rounding": damage,
        "final_damage": final_damage,
    })

    return result


def resolve_attack(attacker, target, board):
    """Calcula el dany, l'aplica i registra les baixes."""
    details = calculate_damage_details(attacker, target)

    if not details["valid"]:
        if board is not None:
            board.last_combat_log = details
        return 0

    # Estat del defensor abans del combat.
    units_before = target.count
    hp_before = target.hp
    alive_before = target.is_alive
    troop_name = target.troop.name

    # Aplicar el dany amb les regles actuals.
    damage = details["final_damage"]
    target.take_damage(damage, board)

    # Estat del defensor després del combat.
    units_after = target.count
    hp_after = target.hp
    alive_after = target.is_alive

    # Afegir el resultat al registre detallat.
    details.update({
        "target_troop": troop_name,
        "target_units_before": units_before,
        "target_units_after": units_after,
        "target_hp_before": hp_before,
        "target_hp_after": hp_after,
        "units_lost": max(0, units_before - units_after),
        "target_eliminated": alive_before and not alive_after,
    })

    if board is not None:
        board.last_combat_log = details

    return damage


def format_combat_columns(details):
    """Retorna el resultat del combat i una explicació del càlcul."""

    if not details or not details.get("valid"):
        return "Atac no vàlid.", ""

    units_before = details.get("target_units_before", 0)
    units_after = details.get("target_units_after", 0)
    units_lost = details.get("units_lost", 0)
    hp_before = details.get("target_hp_before", 0)
    hp_after = details.get("target_hp_after", 0)
    eliminated = details.get("target_eliminated", False)

    # Valors del càlcul
    base = details["base_damage"]
    weapon = details["weapon_modifier"]
    defence = details["defence_modifier"]
    attack_type = details["attack_type_modifier"]
    armor = details["armor_resistance"]
    shield = details["shield_resistance"]
    raw_damage = details["damage_before_rounding"]
    final_damage = details["final_damage"]

    # Resultat del combat
    if eliminated:
        status = "TROPA ELIMINADA"
    elif units_lost > 0:
        status = f"{units_lost} unitat(s) eliminada(es)"
    elif hp_after < hp_before:
        status = "La unitat frontal ha rebut dany"
    else:
        status = "Sense baixes"

    left = (
        "RESULTAT DEL COMBAT\n"
        "--------------------\n"
        f"Objectiu: {details.get('target_troop', 'Tropa')}\n"
        f"Unitats inicials: {units_before}\n"
        f"Dany inflingit: {final_damage}\n"
        f"Unitats perdudes: {units_lost}\n"
        f"Unitats restants: {units_after}\n"
        f"Vida frontal: {hp_before} -> {hp_after}\n"
        "\n"
        f"Estat: {status}"
    )

    # Fórmula desenvolupada pas a pas
    right = (
        "COM S'HA CALCULAT EL DANY?\n"
        "--------------------\n"
        "\n"
        "DANY BASE\n"
        f"Dany de l'atac: {base}\n"
        "\n"
        "MODIFICADORS OFENSIUS\n"
        f"Arma: x{weapon:.2f}\n"
        f"Tipus d'atac ({details['attack_type']}): "
        f"x{attack_type:.2f}\n"
        "\n"
        "MODIFICADOR DEFENSIU\n"
        f"Atac: {details['attack']}\n"
        f"Defensa: {details['defence']}\n"
        f"Modificador: x{defence:.2f}\n"
        "\n"
        "RESISTÈNCIES\n"
        f"Armadura ({details['armor_type']}): "
        f"{armor:.0%} de reducció\n"
        f"Dany restant: x{1 - armor:.2f}\n"
        f"Escut ({details['shield_type']}): "
        f"{shield:.0%} de reducció\n"
        f"Dany restant: x{1 - shield:.2f}\n"
        "\n"
        "RESULTAT\n"
        f"{base} x {weapon:.2f} x {attack_type:.2f}\n"
        f"x {defence:.2f} x {1 - armor:.2f}\n"
        f"x {1 - shield:.2f}\n"
        f"= {raw_damage:.2f} abans d'arrodonir\n"
        f"= {final_damage} de dany final"
    )

    return left, right
