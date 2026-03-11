from pathlib import Path
import extract_msg
import re

from app.domain.models.lead import Lead
from app.domain.parsers.parser_utils import (
    clean_email,
    extract_datetime_from_zapier,
    split_full_name,
)


class PVALARMParser:
    quelle = "PVALARM"

    def parse_file(self, file_path: Path) -> Lead | None:
        file_path = Path(file_path)
        msg = extract_msg.Message(str(file_path))
        body = msg.body or ""
        lines = [line.strip() for line in body.splitlines() if line.strip()]

        data = {}

        for index, line in enumerate(lines):
            match = re.match(r"([^:]+):\s*(.+)", line)

            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                data[key] = value

            elif line.startswith("Thema"):
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    data["Thema"] = parts[1].strip()

            elif index + 1 < len(lines):
                if line.endswith("?"):
                    data[line.strip()] = lines[index + 1].strip()

        full_name = data.get("Name", "")
        vorname, nachname = split_full_name(full_name)
        datum, uhrzeit = extract_datetime_from_zapier(body)

        eigentuemer = data.get("Eigentümer der Immobilie", "")
        speicher = data.get("PF mit Speicher?", "")

        return Lead(
            quelle=self.quelle,
            datum=datum,
            uhrzeit=uhrzeit,
            vorname=vorname,
            nachname=nachname,
            telefon=data.get("Tel", ""),
            email=clean_email(data.get("Email", "")),
            bundesland=data.get("Bundesland", ""),
            finanzierung=data.get("Welche Lösung passt am ehesten zu dir?", ""),
            adresse=f"{data.get('Straße', '')}, {data.get('Plz', '')} {data.get('Ort', '')}".strip(),
            lead_id="",
            technologie=data.get("Thema", ""),
            zeitraum=data.get("Umsetzung", data.get("Wie konkret ist dein Projekt aktuell?", "")),
            besitzverhaeltnis="Eigentümer*in" if "ja" in eigentuemer.lower() else eigentuemer,
            stromspeicher="Ja" if "ja" in speicher.lower() else speicher,
            ergaenzende_informationen=data.get("Warum interessierst du dich jetzt für eine PV-Lösung?", ""),
        )