from dataclasses import dataclass
from typing import Optional


@dataclass
class Project:
    projekt_id: str
    kunde: str
    adresse: str = ""
    mail: str = ""
    telefon: str = ""
    status: str = "Lead"
    status_datum: str = ""
    naechster_schritt: str = ""
    deadline: str = ""
    scoring: str = ""
    notiz: str = ""
    projektordner_pfad: Optional[str] = None