import json
from pathlib import Path

from data.combat_types_data import COMBAT_TYPES


DATA_FILE = Path(__file__).with_name("troops.json")


REQUIRED_FIELDS = {
    "name",
    "symbol",
    "cost",
    "life",
    "attack",
    "defence",
    "damage",
    "movement",
    "attack_range",
    "attack_type",
    "abilities",
}

NUMERIC_FIELDS = (
    "cost",
    "life",
    "attack",
    "defence",
    "damage",
    "movement",
    "attack_range",
)


def validate_numeric_fields(key, data):
    """Valida els camps numèrics d'una tropa."""

    for field in NUMERIC_FIELDS:
        value = data[field]

        if type(value) is not int or value < 0:
            raise ValueError(
                f"'{key}.{field}' ha de ser un enter "
                "major o igual que zero."
            )


def validate_text_field(key, data, field):
    """Valida un camp de text obligatori."""

    value = data[field]

    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"Camp '{field}' no vàlid per a la tropa '{key}'."
        )


def validate_abilities(key, abilities):
    """Valida la llista d'habilitats."""

    if not isinstance(abilities, list):
        raise ValueError(
            f"'abilities' ha de ser una llista a la tropa '{key}'."
        )

    if not all(
        isinstance(ability, str) and ability.strip()
        for ability in abilities
    ):
        raise ValueError(
            f"Les habilitats de '{key}' han de ser noms no buits."
        )


def validate_choice(key, data, field, valid_values, label):
    """Comprova que un valor pertanyi a les opcions permeses."""

    value = data[field]

    if value not in valid_values:
        raise ValueError(
            f"{label} no vàlid a '{key}': {value}"
        )


def validate_combat_fields(key, data):
    """Valida els camps de combat de cada tropa."""

    validate_choice(
        key, data,
        "attack_type",
        COMBAT_TYPES["attack_types"],
        "Tipus d'atac",
    )

    validate_choice(
        key, data,
        "damage_type",
        COMBAT_TYPES["damage_types"],
        "Tipus de dany",
    )

    validate_choice(
        key, data,
        "damage_modifier",
        COMBAT_TYPES["damage_modifiers"],
        "Modificador de dany",
    )

    validate_choice(
        key, data,
        "armor_type",
        COMBAT_TYPES["armor"],
        "Tipus d'armadura",
    )

    validate_choice(
        key, data,
        "armor_modifier",
        COMBAT_TYPES["armor_modifiers"],
        "Modificador d'armadura",
    )

    validate_choice(
        key, data,
        "shield_type",
        COMBAT_TYPES["shields"],
        "Tipus d'escut",
    )

    # Sense escut, el modificador no té efecte.
    if data["shield_type"] == "no_shield":
        data["shield_modifier"] = "unshielded"
    else:
        validate_choice(
            key, data,
            "shield_modifier",
            COMBAT_TYPES["shield_modifiers"],
            "Modificador d'escut",
        )


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

    for key, data in troops.items():

        if not isinstance(data, dict):
            raise ValueError(
                f"La definició de la tropa '{key}' no és vàlida."
            )

        missing = REQUIRED_FIELDS - data.keys()

        if missing:
            raise ValueError(
                f"La tropa '{key}' no té els camps: "
                f"{', '.join(sorted(missing))}"
            )

        validate_numeric_fields(key, data)
        validate_text_field(key, data, "name")
        validate_text_field(key, data, "symbol")
        validate_abilities(key, data["abilities"])
        validate_combat_fields(key, data)

    return troops


TROOPS = load_troops()
