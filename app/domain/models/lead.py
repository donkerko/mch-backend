from dataclasses import dataclass
from typing import Optional


@dataclass
class Lead:
    quelle: str = ""
    datum: str = ""
    uhrzeit: str = ""
    vorname: str = ""
    nachname: str = ""
    adresse: str = ""
    email: str = ""
    telefon: str = ""
    bundesland: str = ""
    bezirk: str = ""
    lead_id: str = ""
    technologie: str = ""
    baustellen_typ: str = ""
    platzierung: str = ""
    dach: str = ""
    flaeche: str = ""
    besitzverhaeltnis: str = ""
    zeitraum: str = ""
    jahresstromverbrauch_kwh: str = ""
    stromspeicher: str = ""
    finanzierung: str = ""
    ergaenzende_informationen: str = ""

    @property
    def full_name(self) -> str:
        return f"{self.vorname} {self.nachname}".strip()