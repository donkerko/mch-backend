from dataclasses import dataclass


@dataclass
class Offer:
    name: str = ""
    angebotsdatum: str = ""
    angerufen_am: str = ""
    kontaktperson: str = ""
    angebot_nr: str = ""
    angebot_pfad: str = ""
    bemerkung: str = ""
    urgieren_am: str = ""

    @property
    def has_required_fields(self) -> bool:
        return bool(self.angebot_nr and self.angebotsdatum and self.name)