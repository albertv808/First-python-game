import json
from pathlib import Path

DATA_FILE = Path(__file__).with_name("combat_types.json")


def load_combat_types():
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"No s'ha trobat el fitxer: {DATA_FILE}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"JSON de combat no vàlid: {exc}"
        ) from exc

    required = {
        "damage_types",
        "damage_modifiers",
        "armor",
        "shields",
        "shield_modifiers",
    }

    missing = required - data.keys()
    if missing:
        raise ValueError(
            f"Falten seccions al JSON: {', '.join(sorted(missing))}"
        )

    for armor_key, resistances in data["armor"].items():
        for damage_type in ("slash", "pierce", "blunt"):
            value = resistances.get(damage_type)
            if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                raise ValueError(
                    f"Resistència no vàlida: armor.{armor_key}.{damage_type}"
                )

    for shield_key, resistances in data["shields"].items():
        for attack_type in ("melee", "ranged"):
            value = resistances.get(attack_type)
            if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                raise ValueError(
                    f"Resistència no vàlida: shields.{shield_key}.{attack_type}"
                )

    return data


COMBAT_TYPES = load_combat_types()