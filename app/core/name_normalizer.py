import re
from app.config.settings import TITLE_TOKENS


def normalize_text(text: str) -> str:
    if not text:
        return ""

    replacements = {
        "ä": "ae", "ö": "oe", "ü": "ue",
        "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
        "ß": "ss",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r'[<>:"/\\|?*]', "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def strip_titles(full_name: str) -> str:
    parts = full_name.split()
    cleaned = []

    for part in parts:
        token = part.lower().strip()
        if token not in TITLE_TOKENS:
            cleaned.append(part)

    return " ".join(cleaned)


def split_name(full_name: str) -> tuple[str, str]:
    full_name = normalize_text(strip_titles(full_name))

    if not full_name:
        return "", ""

    parts = full_name.split()

    if len(parts) == 1:
        return "", parts[0]

    vorname = parts[0]
    nachname = " ".join(parts[1:])
    return vorname, nachname


def build_name_variants(vorname: str, nachname: str) -> list[str]:
    vorname = normalize_text(vorname).lower()
    nachname = normalize_text(nachname).lower()

    variants = []

    if vorname and nachname:
        variants.append(f"{vorname} {nachname}")
        variants.append(f"{nachname} {vorname}")
        variants.append(f"{vorname}{nachname}")
        variants.append(f"{nachname}{vorname}")
    elif nachname:
        variants.append(nachname)

    return list(dict.fromkeys(variants))


def normalize_for_compare(full_name: str) -> str:
    vorname, nachname = split_name(full_name)
    variants = build_name_variants(vorname, nachname)
    return variants[0] if variants else ""