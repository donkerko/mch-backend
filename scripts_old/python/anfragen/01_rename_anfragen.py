import os
import re
import email
import pdfplumber

BASE_PATHS = [
    r"C:\Users\PV\OneDrive\ENKO GmbH\Anfragen\voltalux",
    r"C:\Users\PV\OneDrive\ENKO GmbH\Anfragen\PVALARM",
    r"C:\Users\PV\OneDrive\ENKO GmbH\Anfragen\photovoltaikAT"

]


def clean_filename(name):
    replacements = {
        "ä": "ae", "ö": "oe", "ü": "ue",
        "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
        "ß": "ss"
    }
    for k, v in replacements.items():
        name = name.replace(k, v)

    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.strip()


def extract_lastname_from_text(text):
    patterns = [
        r"Nachname:\s*(\w+)",
        r"Ihr Name\s*[\r\n]+\s*(\w+)",
        r"Name:\s*\w+\s+(\w+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return "Unbekannt"



def extract_from_pdf(path):
    try:
        with pdfplumber.open(path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return extract_lastname_from_text(text)
    except:
        return None


def extract_from_msg(path):
    try:
        with open(path, "rb") as f:
            msg = email.message_from_binary_file(f)

        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode(errors="ignore")
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")
        return extract_lastname_from_text(body)
    except:
        return None


def get_unique_path(path):
    base, ext = os.path.splitext(path)
    counter = 1
    new_path = path

    while os.path.exists(new_path):
        new_path = f"{base}_{counter}{ext}"
        counter += 1

    return new_path


def process_files():

    for base_path in BASE_PATHS:
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if "Unbekannt" not in file:
                    continue

                full_path = os.path.join(root, file)

                lastname = None

                if file.lower().endswith(".pdf"):
                    lastname = extract_from_pdf(full_path)

                elif file.lower().endswith(".msg"):
                    lastname = extract_from_msg(full_path)

                if lastname:
                    lastname = clean_filename(lastname)

                    # Regex: ersetzt _Unbekannt_... vor der Dateiendung
                    if file.lower().endswith(".pdf"):
                        new_name = re.sub(r"_Unbekannt.*(?=\.pdf$)", f"_{lastname}", file)
                    elif file.lower().endswith(".msg"):
                        new_name = re.sub(r"_Unbekannt.*(?=\.msg$)", f"_{lastname}", file)

                    new_path = os.path.join(root, new_name)
                    new_path = get_unique_path(new_path)

                    os.rename(full_path, new_path)
                    print(f"Renamed: {file} -> {new_name}")

                else:
                    print(f"Could not parse: {file}")


if __name__ == "__main__":
    process_files()
