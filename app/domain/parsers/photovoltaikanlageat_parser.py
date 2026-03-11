from pathlib import Path
import extract_msg

from app.domain.models.lead import Lead
from app.domain.parsers.parser_utils import (
    clean_email,
    extract_datetime_from_msg_text,
    split_full_name,
)


class PhotovoltaikanlageATParser:
    quelle = "Photovoltaikanlage.at"
    start_question = "Welche Kategorie trifft auf Sie zu?"

    def parse_file(self, file_path: Path) -> Lead | None:
        file_path = Path(file_path)
        msg = extract_msg.Message(str(file_path))
        body = msg.body or ""
        lines = [line.strip() for line in body.splitlines() if line.strip()]

        start_index = None
        for i, line in enumerate(lines):
            if self.start_question in line:
                start_index = i
                break

        if start_index is None:
            return None

        data = {}

        if any("\t" in line for line in lines):
            for line in lines:
                if "\t" in line:
                    key, value = line.split("\t", 1)
                    if "© Nettbureau" in key:
                        break
                    data[key.strip()] = value.strip()
        else:
            i = start_index
            while i < len(lines) - 1:
                question = lines[i]
                answer = lines[i + 1]
                if "© Nettbureau" in question or "Kontaktieren Sie" in question:
                    break
                data[question] = answer
                i += 2

        full_name = data.get("Ihr Name", "").strip() or data.get("Kontaktperson", "").strip()
        vorname, nachname = split_full_name(full_name)
        datum, uhrzeit = extract_datetime_from_msg_text(body)

        v = data.get("Wie hoch ist Ihr Energieverbrauch pro Jahr ungefähr?", "").strip()
        if v:
            try:
                verbrauch = str(int(v) * 1000) if int(v) < 100 else str(int(v))
            except ValueError:
                verbrauch = ""
        else:
            verbrauch = ""

        return Lead(
            quelle=self.quelle,
            datum=datum,
            uhrzeit=uhrzeit,
            vorname=vorname,
            nachname=nachname,
            adresse=f"{data.get('Adresse', '')} {data.get('Hausnr.', '')}, {data.get('Postleitzahl', '')} {data.get('Ortschaft', '')}".strip(),
            email=clean_email(data.get("E-Mail-Addresse", "")),
            telefon=data.get("Mobile Rufnummer", ""),
            bundesland=data.get("Region", ""),
            bezirk=data.get("Bezirk", ""),
            lead_id="",
            technologie=data.get("Welche Technologie interessiert Sie?", ""),
            besitzverhaeltnis=data.get("Welche Kategorie trifft auf Sie zu?", ""),
            platzierung=data.get("Wo soll das System montiert werden?", ""),
            dach=data.get("Welche Dachform hat das Haus?", ""),
            flaeche=data.get("Wie groß ist die Fläche ungefähr, auf der die Anlage installiert werden soll?", ""),
            baustellen_typ=data.get("Wählen Sie den Gebäudetyp aus.", ""),
            zeitraum=data.get("Wann möchten Sie Ihre Anlage installieren?", ""),
            jahresstromverbrauch_kwh=verbrauch,
            stromspeicher=data.get("Möchten Sie einen Batteriespeicher?", ""),
            finanzierung=data.get("Wie soll die Finanzierung erfolgen?", ""),
            ergaenzende_informationen=data.get("Was möchten Sie uns noch mitteilen?", ""),
        )