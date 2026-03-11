import re
from datetime import datetime
from app.core.name_normalizer import split_name


def clean_email(raw_email: str) -> str:
    if not raw_email:
        return ""

    match = re.search(r"[\w\.-]+@[\w\.-]+", raw_email)
    if match:
        return match.group(0).strip()

    return raw_email.strip()


def get_question_value(lines: list[str], question: str) -> str:
    for i, line in enumerate(lines):
        if line.startswith(question):
            if "?" in line:
                parts = line.split("?", 1)
                if parts[1].strip():
                    return parts[1].strip()
            elif i + 1 < len(lines):
                return lines[i + 1].strip()
            return ""
    return ""


def extract_kwh(text: str):
    if not text:
        return ""

    match = re.search(r"(\d[\d\.]*)\s*kwh", text.lower())
    if not match:
        return ""

    value = match.group(1).replace(".", "")
    return value


def extract_datetime_from_msg_text(text: str) -> tuple[str, str]:
    match = re.search(r"Empfangen\s+(\d{4}-\d{2}-\d{2})\s+kl\.\s+(\d{2}:\d{2})", text)
    if not match:
        return "", ""

    dt = datetime.strptime(f"{match.group(1)} {match.group(2)}", "%Y-%m-%d %H:%M")
    return dt.date().isoformat(), dt.time().strftime("%H:%M:%S")


def extract_datetime_from_zapier(text: str) -> tuple[str, str]:
    match = re.search(r"Zeit:\s*(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})", text)
    if not match:
        return "", ""

    dt = datetime.strptime(f"{match.group(1)} {match.group(2)}", "%Y-%m-%d %H:%M:%S")
    return dt.date().isoformat(), dt.time().strftime("%H:%M:%S")


def extract_datetime_from_pdf_text(text: str) -> tuple[str, str]:
    match = re.search(r"Am\s+(\d{2}\.\d{2}\.\d{4})\s+um\s+(\d{2}:\d{2})", text)
    if not match:
        return "", ""

    dt = datetime.strptime(f"{match.group(1)} {match.group(2)}", "%d.%m.%Y %H:%M")
    return dt.date().isoformat(), dt.time().strftime("%H:%M:%S")


def split_full_name(full_name: str) -> tuple[str, str]:
    return split_name(full_name)