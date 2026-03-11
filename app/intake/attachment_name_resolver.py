from pathlib import Path
import re
import pdfplumber
import extract_msg

from app.core.name_normalizer import split_name


class AttachmentNameResolver:
    def resolve_from_pdf(self, pdf_path: Path) -> tuple[str, str]:
        text = ""

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"

        vorname = ""
        nachname = ""

        match_vorname = re.search(r"Vorname:\s*(.+)", text, re.IGNORECASE)
        match_nachname = re.search(r"Nachname:\s*(.+)", text, re.IGNORECASE)

        if match_vorname:
            vorname = match_vorname.group(1).strip().splitlines()[0]
        if match_nachname:
            nachname = match_nachname.group(1).strip().splitlines()[0]

        if vorname or nachname:
            return split_name(f"{vorname} {nachname}".strip())

        fallback_patterns = [
            r"Ihr Name\s*[\r\n]+\s*(.+)",
            r"Name:\s*(.+)",
        ]

        for pattern in fallback_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return split_name(match.group(1).strip())

        return "", ""

    def resolve_from_msg(self, msg_path: Path) -> tuple[str, str]:
        msg = extract_msg.Message(str(msg_path))
        body = msg.body or ""

        patterns = [
            r"Ihr Name\s*[\r\n]+\s*(.+)",
            r"Kontaktperson\s*[\r\n]+\s*(.+)",
            r"Name:\s*(.+)",
            r"Name\s*[\r\n]+\s*(.+)",
            r"Nachname:\s*(.+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                return split_name(match.group(1).strip())

        return "", ""

    def resolve_from_attachment_file(self, file_path: Path) -> tuple[str, str]:
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return self.resolve_from_pdf(file_path)

        if suffix == ".msg":
            return self.resolve_from_msg(file_path)

        return "", ""