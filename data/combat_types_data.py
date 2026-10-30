import json
import math
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).with_name("combat_types.json")

REQUIRED_SECTIONS = {
    "damage_types",
    "attack_types",
    "attack_type_modifiers",
    "damage_modifiers",
    "armor",
    "armor_modifiers",
    "shields",
    "shield_modifiers",
}

DAMAGE_TYPES = ("slash", "pierce", "blunt")
ATTACK_TYPES = ("melee", "ranged")
ARMOR_LEVELS = ("unarmored", "light", "medium", "heavy")
DAMAGE_LEVELS = ("light", "medium", "heavy")
SHIELD_LEVELS = ("unshielded", "light", "medium", "heavy")


def _validate_mapping(data: dict[str, Any], section: str) -> dict:
    """Comprova que una secció existeix i és un diccionari."""
    value = data.get(section)

    if not isinstance(value, dict):
        raise ValueError(
            f"La secció '{section}' ha de ser un objecte JSON."
        )

    if not value:
        raise ValueError(
            f"La secció '{section}' no pot estar buida."
        )

    return value


def _validate_required_keys(
    data: dict,
    section: str,
    expected: tuple[str, ...],
) -> None:
    entries = _validate_mapping(data, section)
    missing = set(expected) - entries.keys()

    if missing:
        raise ValueError(
            f"Falten claus a '{section}': {', '.join(sorted(missing))}"
        )


def _validate_number(
    value: Any,
    path: str,
    minimum: float | None = None,
    maximum: float | None = None,
) -> None:
    """Valida un valor numèric i, opcionalment, els seus límits."""
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise ValueError(f"Valor numèric no vàlid: {path}")

    if minimum is not None and value < minimum:
        raise ValueError(f"Valor massa petit: {path}")

    if maximum is not None and value > maximum:
        raise ValueError(f"Valor massa gran: {path}")


def _validate_resistances(
    data: dict[str, Any],
    section: str,
    types: tuple[str, ...],
) -> None:
    """Valida les resistències de cada armadura o escut."""
    entries = _validate_mapping(data, section)

    for name, resistances in entries.items():
        if not isinstance(resistances, dict):
            raise ValueError(
                f"'{section}.{name}' ha de ser un objecte JSON."
            )

        for damage_type in types:
            if damage_type not in resistances:
                raise ValueError(
                    f"Falta el camp '{section}.{name}.{damage_type}'."
                )

            _validate_number(
                resistances[damage_type],
                f"{section}.{name}.{damage_type}",
                minimum=0,
                maximum=1,
            )


def _validate_modifiers(
    data: dict[str, Any],
    section: str,
    minimum: float = 0,
) -> None:
    """Valida els modificadors numèrics d'una secció."""
    modifiers = _validate_mapping(data, section)

    for name, value in modifiers.items():
        _validate_number(
            value,
            f"{section}.{name}",
            minimum=minimum,
        )


def load_combat_types() -> dict[str, Any]:
    """Carrega i valida la configuració dels tipus de combat."""
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

    if not isinstance(data, dict):
        raise ValueError(
            "El fitxer JSON ha de contenir un objecte a l'arrel."
        )

    missing = REQUIRED_SECTIONS - data.keys()
    if missing:
        raise ValueError(
            f"Falten seccions al JSON: {', '.join(sorted(missing))}"
        )

    # Validació de les seccions que contenen identificadors i noms.
    for section in ("damage_types", "attack_types"):
        entries = _validate_mapping(data, section)

        for key, label in entries.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError(
                    f"Identificador no vàlid a '{section}'."
                )

            if not isinstance(label, str) or not label.strip():
                raise ValueError(
                    f"Nom no vàlid: {section}.{key}"
                )

    # Resistències de les armadures i els escuts.
    _validate_resistances(data, "armor", DAMAGE_TYPES)
    _validate_resistances(data, "shields", ATTACK_TYPES)

    # Validacio de les claus dels valors modificadors.
    _validate_required_keys(data, "damage_modifiers", DAMAGE_LEVELS)
    _validate_required_keys(data, "armor_modifiers", ARMOR_LEVELS)
    _validate_required_keys(data, "shield_modifiers", SHIELD_LEVELS)

    # Modificadors numèrics.
    _validate_modifiers(data, "attack_type_modifiers")
    _validate_modifiers(data, "damage_modifiers")
    _validate_modifiers(data, "armor_modifiers")
    _validate_modifiers(data, "shield_modifiers")

    # Comprova que els modificadors cobreixen els tipus declarats.
    for section in (
        "attack_type_modifiers",
        "damage_modifiers",
        "armor_modifiers",
        "shield_modifiers",
    ):
        expected_types = {
            "attack_type_modifiers": data["attack_types"],
            "damage_modifiers": None,
            "armor_modifiers": None,
            "shield_modifiers": None,
        }[section]

        if expected_types is not None:
            missing_types = expected_types.keys() - data[section].keys()
            if missing_types:
                raise ValueError(
                    f"Falten modificadors a '{section}': "
                    f"{', '.join(sorted(missing_types))}"
                )

    return data


COMBAT_TYPES = load_combat_types()
