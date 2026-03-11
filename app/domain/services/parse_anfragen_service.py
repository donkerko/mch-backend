class ParseAnfragenService:
    def __init__(self, anfragen_repository, logger):
        self.anfragen_repository = anfragen_repository
        self.logger = logger

    def _build_unique_key(self, lead):
        if lead.lead_id:
            return lead.lead_id.strip().lower()

        if lead.email:
            return lead.email.strip().lower()

        if lead.nachname and lead.datum and lead.uhrzeit:
            return f"sha:{lead.nachname.strip().lower()}|{lead.datum}|{lead.uhrzeit}".lower()

        return ""

    def import_lead(self, lead, source_file: str) -> bool:
        if lead is None:
            self.logger.log_global("SYSTEM", f"Übersprungen: {source_file} (Parser lieferte None)")
            return False

        unique_key = self._build_unique_key(lead)
        if not unique_key:
            self.logger.log_global(lead.full_name or "UNBEKANNT", f"Übersprungen: {source_file} (kein eindeutiger Schlüssel)")
            return False

        existing_keys = self.anfragen_repository.get_existing_keys()

        if unique_key in existing_keys:
            self.logger.log_global(lead.full_name or "UNBEKANNT", f"Dublette erkannt: {source_file}")
            return False

        self.anfragen_repository.append_lead(lead)
        self.logger.log_global(lead.full_name or "UNBEKANNT", f"Lead importiert aus {source_file}")
        return True