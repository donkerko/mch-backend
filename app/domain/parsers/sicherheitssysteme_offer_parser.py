from pathlib import Path
import re

import pdfplumber

from app.domain.models.offer import Offer


class SicherheitssystemeOfferParser:
    """
    Parser für Angebot-PDFs von Sicherheitssysteme Vöcklabruck GmbH.

    Ziel:
    - Name
    - Kontaktperson
    - Angebotsdatum
    - Angebotsnummer

    Heuristik:
    - Angebotsnummer nur bevorzugt aus Zeilen mit "Angebot:"
    - Datum nur bevorzugt aus Zeilen mit "Datum:"
    - Kundenblock wird im Kopfbereich vor "Angebot:" gesucht
    - Privatkunde:
        [Person]
        [Straße]
        [PLZ Ort]
    - Firma ohne Ansprechpartner:
        [Firma]
        [UID: ...] optional
        [Firma] Marker optional
        [Straße]
        [PLZ Ort]
    - Firma mit Ansprechpartner:
        [Firma]
        [Ansprechpartner]
        [Straße]
        [PLZ Ort]
    """

    def parse(self, pdf_path: Path) -> Offer:
        pdf_path = Path(pdf_path)

        raw_text = self._extract_text(pdf_path)
        lines = self._clean_lines(raw_text)

        angebot_nr = self._extract_angebot_nr(lines)
        angebotsdatum = self._extract_date(lines)
        name, kontaktperson = self._extract_recipient_block(lines)

        print("ANGEBOTSNUMMER:", angebot_nr)
        print("DATUM:", angebotsdatum)
        print("NAME:", name)
        print("KONTAKTPERSON:", kontaktperson)
        
        return Offer(
            name=name,
            kontaktperson=kontaktperson,
            angebotsdatum=angebotsdatum,
            angebot_nr=angebot_nr,
        )

    def _extract_text(self, pdf_path: Path) -> str:
        text_parts: list[str] = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        return "\n".join(text_parts)

    def _clean_lines(self, text: str) -> list[str]:
        return [line.strip() for line in text.splitlines() if line.strip()]

    def _extract_angebot_nr(self, lines: list[str]) -> str:
        # 1. Beste Quelle: "Angebot: An-VB-..."
        for line in lines:
            match = re.match(r"^Angebot:\s*(An-[A-Za-z0-9/-]+)$", line, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # 2. Fallback: "Angebot An-VB-..."
        for line in lines:
            match = re.match(r"^Angebot\s+(An-[A-Za-z0-9/-]+)$", line, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # 3. Letzter Fallback: erste vorkommende AN-Nummer
        for line in lines:
            match = re.search(r"\b(An-[A-Za-z0-9/-]+)\b", line, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_date(self, lines: list[str]) -> str:
        # 1. Beste Quelle: "Datum: dd.mm.yyyy"
        for line in lines:
            match = re.match(r"^Datum:\s*(\d{2}\.\d{2}\.\d{4})$", line, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # 2. Fallback: erste Datum-Zeichenfolge
        for line in lines:
            match = re.search(r"\b(\d{2}\.\d{2}\.\d{4})\b", line)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_recipient_block(self, lines: list[str]) -> tuple[str, str]:
        """
        Returns:
            (name, kontaktperson)

        Regeln:
        - Suche nur im Kopfbereich vor der ersten "Angebot:"-Zeile
        - Finde rückwärts den Block mit:
            [Straße]
            [PLZ Ort]
        - Interpretiere die relevanten Zeilen darüber
        """
        angebot_index = self._find_first_angebot_index(lines)
        header_lines = lines[:angebot_index] if angebot_index is not None else lines[:20]

        # Suche rückwärts nach:
        # prev = Straße
        # current = PLZ/Ort
        for i in range(len(header_lines) - 1, 1, -1):
            current_line = header_lines[i]
            prev_line = header_lines[i - 1]

            if self._looks_like_postcode_city(current_line) and self._looks_like_street(prev_line):
                candidates = self._collect_candidate_lines_above_address(header_lines, i - 1)

                if not candidates:
                    return "", ""

                # Fall 1: nur 1 relevante Zeile über der Adresse
                if len(candidates) == 1:
                    candidate = candidates[0]

                    if self._looks_like_company_name(candidate):
                        return candidate.strip(), ""

                    cleaned = self._clean_person_name(candidate)
                    return cleaned, cleaned

                # Fall 2: mehrere relevante Zeilen
                # Wir nehmen die letzten zwei sinnvollen Kandidaten
                first = candidates[-2]
                second = candidates[-1]

                # Firma + Ansprechpartner
                if self._looks_like_company_name(first):
                    return first.strip(), self._clean_person_name(second)

                # Sonderfall: "Firma" Marker ist bereits entfernt, dann bleibt u.U. nur der Firmenname
                if self._looks_like_company_name(second):
                    return second.strip(), ""

                # Sonst wie Privatperson behandeln
                cleaned = self._clean_person_name(second)
                return cleaned, cleaned

        return "", ""

    def _find_first_angebot_index(self, lines: list[str]) -> int | None:
        for i, line in enumerate(lines):
            if line.startswith("Angebot:"):
                return i
        return None

    def _collect_candidate_lines_above_address(self, header_lines: list[str], street_index: int) -> list[str]:
        """
        Sammelt relevante Kandidaten oberhalb der Straßenzeile.

        street_index zeigt auf die Straßenzeile.
        Wir schauen einige Zeilen darüber und filtern:
        - Absenderdaten raus
        - interne Felder raus
        - Kundentypmarker raus
        """
        start = max(0, street_index - 5)
        window = header_lines[start:street_index]

        candidates: list[str] = []
        for line in window:
            if self._is_sender_line(line):
                continue
            if self._is_internal_meta_line(line):
                continue
            if self._is_customer_type_marker(line):
                continue
            if self._is_customer_uid_line(line):
                continue
            candidates.append(line)

        return candidates

    def _looks_like_street(self, line: str) -> bool:
        street_tokens = [
            "straße", "str.", "strasse", "weg", "gasse", "platz", "allee"
        ]
        lower = line.lower()
        return any(token in lower for token in street_tokens)

    def _looks_like_postcode_city(self, line: str) -> bool:
        return bool(re.search(r"\b\d{4,5}\b", line))

    def _looks_like_company_name(self, line: str) -> bool:
        company_tokens = [
            "gmbh", "ag", "kg", "og", "e.u.", "eu", "gesmbh", "mbh"
        ]
        lower = line.lower()
        return any(token in lower for token in company_tokens)

    def _is_sender_line(self, line: str) -> bool:
        sender_markers = [
            "Sicherheitssysteme Vöcklabruck GmbH",
            "Linzer Straße",
            "4840 Vöcklabruck",
            "Österreich",
            "Tel.:",
            "office.vb@",
            "Firmenbuch:",
            "Raiffeisenbank",
            "Sparkasse",
            "UID: ATU 53187402",  # bekannte UID vom Absender
        ]
        lower = line.lower()
        return any(marker.lower() in lower for marker in sender_markers)

    def _is_internal_meta_line(self, line: str) -> bool:
        internal_prefixes = [
            "Datum:",
            "gültig bis:",
            "Sachbearbeiter:",
            "Komm:",
            "Kundennummer:",
            "Angebot",
        ]
        lower = line.lower()
        return any(lower.startswith(prefix.lower()) for prefix in internal_prefixes)

    def _is_customer_uid_line(self, line: str) -> bool:
        # Kunden-UID soll nicht als Firmenname/Kontaktperson verwendet werden
        return line.lower().startswith("uid:")

    def _is_customer_type_marker(self, line: str) -> bool:
        # Beispiel: "Firma"
        return line.strip().lower() in {"firma"}

    def _clean_person_name(self, line: str) -> str:
        line = line.strip()

        # Anreden entfernen
        for prefix in ["Herr ", "Herrn ", "Frau "]:
            if line.startswith(prefix):
                line = line[len(prefix):].strip()

        # Titel wiederholt am Anfang entfernen
        changed = True
        while changed:
            changed = False
            for title in ["Dr. ", "Mag. ", "Ing. "]:
                if line.startswith(title):
                    line = line[len(title):].strip()
                    changed = True

        return line