from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import Font

from app.domain.models.offer import Offer


class OfferTrackingRepository:
    def __init__(self, file_path: Path, sheet_name: str | None = None):
        self.file_path = Path(file_path)
        self.sheet_name = sheet_name

    def _get_ws(self):
        wb = load_workbook(self.file_path)
        ws = wb[self.sheet_name] if self.sheet_name else wb.active
        return wb, ws

    def get_headers(self) -> list[str]:
        wb, ws = self._get_ws()
        return [cell.value for cell in ws[1]]

    def get_existing_offer_numbers(self) -> set[str]:
        wb, ws = self._get_ws()
        headers = [cell.value for cell in ws[1]]
        if "AN.-Nr.:" not in headers:
            raise ValueError("Excel must contain column 'AN.-Nr.:'")

        offer_index = headers.index("AN.-Nr.:")
        existing = set()

        for row in ws.iter_rows(min_row=2, values_only=True):
            offer_nr = row[offer_index]
            if offer_nr:
                existing.add(str(offer_nr).strip().lower())

        return existing

    def append_offer(self, offer: Offer) -> None:
        wb, ws = self._get_ws()
        headers = [cell.value for cell in ws[1]]

        row_map = {
            "Name": offer.name,
            "Angebotsdatum": offer.angebotsdatum,
            "angerufen am": offer.angerufen_am,
            "Kontaktperson": offer.kontaktperson,
            "AN.-Nr.:": offer.angebot_nr,
            "Angebot": offer.angebot_pfad,
            "Bemerkung": offer.bemerkung,
            "urgieren am": offer.urgieren_am,
        }

        new_row = [row_map.get(header, "") for header in headers]
        ws.append(new_row)

        # hyperlink handling for "Angebot"
        if "Angebot" in headers and offer.angebot_pfad:
            angebot_col = headers.index("Angebot") + 1
            row_number = ws.max_row
            cell = ws.cell(row=row_number, column=angebot_col)
            cell.value = "Öffnen"
            cell.hyperlink = offer.angebot_pfad
            cell.font = Font(color="0000FF", underline="single")

        wb.save(self.file_path)