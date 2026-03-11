import re
from pathlib import Path
from app.core.name_normalizer import normalize_text


def slug(text: str) -> str:
    text = normalize_text(text).lower()
    text = text.replace(" ", "_")
    text = re.sub(r"[^a-z0-9_-]", "", text)
    return text.strip("_")


def build_unknown_token(mail) -> str:
    entry_id = getattr(mail, "EntryID", "") or ""
    if entry_id:
        return entry_id[:8].lower()
    return "unknown"


def ensure_unique_path(target_path: Path) -> Path:
    target_path = Path(target_path)

    if not target_path.exists():
        return target_path

    parent = target_path.parent
    stem = target_path.stem
    suffix = target_path.suffix

    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1