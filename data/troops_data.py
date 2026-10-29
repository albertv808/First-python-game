import json
from pathlib import Path

from data.combat_types_data import COMBAT_TYPES


DATA_FILE = Path(__file__).with_name("troops.json")


# Valors per defecte per mantenir la compatibilitat amb el JSON antic.
DEFAULT_COMBAT_FIELDS = {
    "damage_type": "slash",
    "damage_modifier": "medium",
    "armor_type": "unarmored",
    "armor_modifier": "light",
    "shield_type": "no_shield",
    "shield_modifier": None,
}


def load_troops():
    """Carrega i valida les dades de les tropes."""

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            troops = json.load(file)

    except FileNotFoundError as exc:
        raise RuntimeError(
            f"No s'ha trobat el fitxer de tropes: {DATA_FILE}"
        ) from exc

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"El JSON de tropes no és vàlid: {exc}"
        ) from exc

    if not isinstance(troops, dict):
        raise ValueError(
            "El fitxer de tropes ha de contenir un objecte JSON."
        )

    required_fields = {
        "name",
        "symbol",
        "cost",
        "life",
        "attack",
        "defence",
        "damage",
        "movement",
        "attack_range",
        "abilities",
    }

    combat_fields = {
        "damage_type",
        "damage_modifier",
        "armor_type",
        "armor_modifier",
        "shield_type",
        "shield_modifier",
    }

    for key, data in troops.items():

        if not isinstance(data, dict):
            raise ValueError(
                f"La definició de la tropa '{key}' no és vàlida."
            )

        # Comprovació dels camps originals.
        missing = required_fields - data.keys()

        if missing:
            raise ValueError(
                f"La tropa '{key}' no té els camps: "
                f"{', '.join(sorted(missing))}"
            )

        # Afegim els camps nous si encara no existeixen.
        for field, default_value in DEFAULT_COMBAT_FIELDS.items():
            data.setdefault(field, default_value)

        # Validació dels camps numèrics originals.
        for field in (
            "cost",
            "life",
            "attack",
            "defence",
            "damage",
            "movement",
            "attack_range",
        ):
            value = data[field]

            if type(value) is not int or value < 0:
                raise ValueError(
                    f"'{key}.{field}' ha de ser un enter "
                    "major o igual que zero."
                )

        # Validació del nom i del símbol.
        if not isinstance(data["name"], str) or not data["name"]:
            raise ValueError(
                f"Nom no vàlid per a la tropa '{key}'."
            )

        if not isinstance(data["symbol"], str) or not data["symbol"]:
            raise ValueError(
                f"Símbol no vàlid per a la tropa '{key}'."
            )

        # Validació de les habilitats.
        if not isinstance(data["abilities"], list):
            raise ValueError(
                f"'abilities' ha de ser una llista a la tropa '{key}'."
            )

        if not all(
            isinstance(ability, str) and ability
            for ability in data["abilities"]
        ):
            raise ValueError(
                f"Les habilitats de '{key}' han de ser noms no buits."
            )

        # Validació dels tipus de dany i dels seus modificadors.
        if data["damage_type"] not in COMBAT_TYPES["damage_types"]:
            raise ValueError(
                f"Tipus de dany no vàlid a '{key}': "
                f"{data['damage_type']}"
            )

        if data["damage_modifier"] not in COMBAT_TYPES["damage_modifiers"]:
            raise ValueError(
                f"Modificador de dany no vàlid a '{key}': "
                f"{data['damage_modifier']}"
            )

        # Validació de l'armadura.
        if data["armor_type"] not in COMBAT_TYPES["armor"]:
            raise ValueError(
                f"Tipus d'armadura no vàlid a '{key}': "
                f"{data['armor_type']}"
            )

        if data["armor_type"] == "unarmored":
            # Sense armadura, no existeix cap modificador.
            data["armor_modifier"] = None

        elif data["armor_modifier"] not in COMBAT_TYPES["damage_modifiers"]:
            raise ValueError(
                f"Modificador d'armadura no vàlid a '{key}': "
                f"{data['armor_modifier']}"
            )

        # Validació de l'escut.
        if data["shield_type"] not in COMBAT_TYPES["shields"]:
            raise ValueError(
                f"Tipus d'escut no vàlid a '{key}': "
                f"{data['shield_type']}"
            )

        if data["shield_type"] == "no_shield":
            # Una tropa sense escut no necessita modificador.
            data["shield_modifier"] = None

        elif data["shield_modifier"] not in COMBAT_TYPES["shield_modifiers"]:
            raise ValueError(
                f"Modificador d'escut no vàlid a '{key}': "
                f"{data['shield_modifier']}"
            )

        # Evitem camps inesperats només si volem validar-los
        # estrictament; no els eliminem per preservar extensions futures.

    return troops


TROOPS = load_troops()