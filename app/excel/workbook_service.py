from pathlib import Path
from openpyxl import load_workbook


class WorkbookService:
    @staticmethod
    def open(path: Path):
        return load_workbook(path)

    @staticmethod
    def save(workbook, path: Path) -> None:
        workbook.save(path)