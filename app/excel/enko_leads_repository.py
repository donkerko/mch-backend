from pathlib import Path
from openpyxl import load_workbook
from app.domain.models.lead import Lead


class ENKOLeadsRepository:
    def __init__(self, file_path: Path, sheet_name: str = None):
        self.file_path = Path(file_path)
        self.sheet_name = sheet_name

    def _get_ws(self):
        wb = load_workbook(self.file_path)
        ws = wb[self.sheet_name] if self.sheet_name else wb.active
        return wb, ws

    def append_lead(self, lead: Lead) -> None:
        wb, ws = self._get_ws()

        ws.append([
            lead.lead_datum,
            lead.full_name,
            lead.adresse,
            lead.telefon,
            lead.email,
            lead.quelle,
            lead.notiz,
        ])

        wb.save(self.file_path)