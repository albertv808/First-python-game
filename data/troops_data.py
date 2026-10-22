import json
from pathlib import Path


DATA_FILE = Path(__file__).with_name("troops.json")

def load_troops():
    """Carrega i valida les dades bàsiques de les tropes."""

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

    for key, data in troops.items():
        if not isinstance(data, dict):
            raise ValueError(
                f"La definició de la tropa '{key}' no és vàlida."
            )

        missing = required_fields - data.keys()

        if missing:
            raise ValueError(
                f"La tropa '{key}' no té els camps: "
                f"{', '.join(sorted(missing))}"
            )

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

        if not isinstance(data["name"], str) or not data["name"]:
            raise ValueError(f"Nom no vàlid per a la tropa '{key}'.")

        if not isinstance(data["symbol"], str) or not data["symbol"]:
            raise ValueError(f"Símbol no vàlid per a la tropa '{key}'.")

        if not isinstance(data["abilities"], list):
            raise ValueError(
                f"'abilities' ha de ser una llista a la tropa '{key}'."
            )

    return troops


TROOPS = load_troops()