from pathlib import Path
from openpyxl import load_workbook
from app.domain.models.project import Project


class CRMRepository:
    def __init__(self, file_path: Path, sheet_name: str = None):
        self.file_path = Path(file_path)
        self.sheet_name = sheet_name

    def _get_ws(self):
        wb = load_workbook(self.file_path)
        ws = wb[self.sheet_name] if self.sheet_name else wb.active
        return wb, ws

    def append_project(self, project: Project) -> None:
        wb, ws = self._get_ws()

        ws.append([
            project.projekt_id,
            project.kunde,
            project.adresse,
            project.mail,
            project.telefon,
            project.status,
            project.status_datum,
            project.naechster_schritt,
            project.deadline,
            project.scoring,
            project.notiz,
            project.projektordner_pfad,
        ])

        wb.save(self.file_path)