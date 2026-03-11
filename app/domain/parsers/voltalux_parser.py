import pdfplumber
from pathlib import Path

from app.domain.models.lead import Lead
from app.domain.parsers.parser_utils import (
    extract_datetime_from_pdf_text,
    get_question_value,
    extract_kwh,
)


class VoltaluxParser:
    quelle = "Voltalux"

    def parse_file(self, file_path: Path) -> Lead:
        file_path = Path(file_path)

        with pdfplumber.open(file_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

        lines = [line.strip() for line in full_text.splitlines() if line.strip()]
        datum, uhrzeit = extract_datetime_from_pdf_text(full_text)

        def get_colon_value(label: str) -> str:
            for line in lines:
                if line.startswith(label + ":"):
                    return line.split(":", 1)[1].strip()
            return ""

        return Lead(
            quelle=self.quelle,
            datum=datum,
            uhrzeit=uhrzeit,
            vorname=get_colon_value("Vorname"),
            nachname=get_colon_value("Nachname"),
            adresse=get_colon_value("Adresse"),
            email=get_colon_value("E-Mail"),
            telefon=get_colon_value("Telefon"),
            bundesland=get_colon_value("Bundesland"),
            bezirk=get_colon_value("Bezirk"),
            lead_id=get_colon_value("Lead ID"),
            baustellen_typ=get_question_value(lines, "Wo soll Ihre Photovoltaik Anlage installiert werden?"),
            platzierung=get_question_value(lines, "Auf welcher Fläche soll die Photovoltaik Anlage installiert werden?"),
            besitzverhaeltnis=get_question_value(lines, "Sind Sie Eigentümer*in der Immobilie?"),
            zeitraum=get_question_value(lines, "Wann soll die Anlage installiert werden?"),
            jahresstromverbrauch_kwh=extract_kwh(
                get_question_value(lines, "Wie hoch ist ihr durchschnittlicher Jahresstromverbrauch?")
            ),
            stromspeicher="Ja" if "Mit Stromspeicher" in get_question_value(
                lines, "Möchten Sie die Photovoltaik Anlage mit einem Stromspeicher ergänzen?"
            ) else "Nein",
            finanzierung=get_question_value(lines, "Wie wird die Anschaffung der Anlage finanziert?"),
            ergaenzende_informationen=get_question_value(lines, "Zusätzliche Anmerkungen"),
        )