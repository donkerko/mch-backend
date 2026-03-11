import os
import pdfplumber
import re
import win32com.client
from datetime import datetime
from pathlib import Path

# ==========================
# CONFIG
# ==========================

MAILBOX_NAME = "huetter@enko.at"
FOLDER_NAME = "Auftragsbestätigungen"

BASE_PROJECT_PATH = r"C:\Users\PV\OneDrive\ENKO GmbH\Projekte"
GLOBAL_LOG_PATH = r"C:\Users\PV\OneDrive\backend\logs\auftragsbestaetigungen_log.txt"

PROCESSED_CATEGORY = "Processed"

# ==========================
# HELPERS
# ==========================

def log_global(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(GLOBAL_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def normalize_name(name):
    name = name.lower()

    # remove titles
    titles = ["mag.", "dr.", "bsc.", "msc.", "ing."]
    for t in titles:
        name = name.replace(t, "")

    # umlauts
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss"
    }
    for k, v in replacements.items():
        name = name.replace(k, v)

    name = re.sub(r"\s+", " ", name).strip()
    return name


def classify_attachment(filename):
    fname = filename.lower()

    if "ab-" in fname:
        return "05_Auftrag"
    elif "re-" in fname:
        return "06_Rechnung"
    elif "angebot" in fname:
        return "04_Angebot"
    else:
        return "05_Auftrag"


def ensure_project_structure(project_path):
    subfolders = [
        "01_Lead",
        "02_Datenaufnahme",
        "03_Planung",
        "04_Angebot",
        "05_Auftrag",
        "06_Rechnung",
        "99_Archiv"
    ]

    for folder in subfolders:
        os.makedirs(os.path.join(project_path, folder), exist_ok=True)


def save_with_timestamp_if_exists(target_path):
    if not os.path.exists(target_path):
        return target_path

    base, ext = os.path.splitext(target_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base}_{timestamp}{ext}"


def find_or_create_project_folder(customer_name):
    normalized_customer = normalize_name(customer_name)

    for folder in os.listdir(BASE_PROJECT_PATH):
        folder_path = os.path.join(BASE_PROJECT_PATH, folder)

        if not os.path.isdir(folder_path):
            continue

        normalized_folder = normalize_name(folder)

        if (
            normalized_customer in normalized_folder
            or normalized_folder in normalized_customer
        ):
            return folder_path

    # If not found, create new
    new_path = os.path.join(BASE_PROJECT_PATH, customer_name)
    ensure_project_structure(new_path)
    log_global(f"Created new project folder: {customer_name}")
    return new_path


# def extract_customer_from_mail(mail):
#     # Try subject
#     subject = mail.Subject or ""
#     body = mail.Body or ""

#     combined = subject + " " + body

#     # Very basic name detection (can extend later)
#     match = re.search(r"([A-ZÄÖÜ][a-zäöüß]+)\s([A-ZÄÖÜ][a-zäöüß]+)", combined)
#     if match:
#         return match.group(0)

#     return "Unbekannt"

def extract_name_from_ab_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    for i in range(len(lines) - 3):
        name_line = lines[i]
        street_line = lines[i + 1]
        plz_line = lines[i + 2]
        country_line = lines[i + 3]

        # Street contains number
        if not re.search(r"\d", street_line):
            continue

        # PLZ line contains 4-5 digit number
        if not re.search(r"\b\d{4,5}\b", plz_line):
            continue

        # Country check
        if "österreich" not in country_line.lower():
            continue

        # Clean name line
        name_line = re.sub(r"^(Herrn|Herr|Frau|Familie)\s+", "", name_line, flags=re.IGNORECASE)

        # Only take first two words (Firstname Lastname)
        parts = name_line.split()

        if len(parts) >= 2:
            firstname = parts[0]
            lastname = parts[1]
            return f"{firstname} {lastname}"

    return None


# ==========================
# MAIN
# ==========================

def process_mails():
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    mailbox = outlook.Folders[MAILBOX_NAME]
    folder = mailbox.Folders[FOLDER_NAME]

    for mail in folder.Items:
        try:
            if PROCESSED_CATEGORY in str(mail.Categories):
                continue

            if mail.Attachments.Count == 0:
                continue

            # --- Find AB attachment ---
            ab_attachment = None
            for attachment in mail.Attachments:
                if "ab-" in attachment.FileName.lower() and attachment.FileName.lower().endswith(".pdf"):
                    ab_attachment = attachment
                    break

            if not ab_attachment:
                log_global("ERROR | NO AB FOUND | Mail skipped")
                continue

            # --- Temp save AB ---
            temp_path = os.path.join(BASE_PROJECT_PATH, "_temp_ab.pdf")
            ab_attachment.SaveAsFile(temp_path)

            customer_name = extract_name_from_ab_pdf(temp_path)

            os.remove(temp_path)

            if not customer_name:
                log_global("ERROR | NAME EXTRACTION FAILED | Mail skipped")
                continue

            project_path = find_or_create_project_folder(customer_name)

            project_log_path = os.path.join(project_path, "automation_log.txt")

            # Save attachments to project folder 
            for attachment in mail.Attachments:
                filename = attachment.FileName
                subfolder = classify_attachment(filename)

                target_folder = os.path.join(project_path, subfolder)
                os.makedirs(target_folder, exist_ok=True)

                target_path = os.path.join(target_folder, filename)
                target_path = save_with_timestamp_if_exists(target_path)

                attachment.SaveAsFile(target_path)

                log_message = f"Saved {filename} to {subfolder}"
                log_global(log_message)

                with open(project_log_path, "a", encoding="utf-8") as pf:
                    pf.write(f"{datetime.now()} - {log_message}\n")

            # Add processed category
            existing_categories = mail.Categories or ""
            if existing_categories:
                mail.Categories = existing_categories + ";" + PROCESSED_CATEGORY
            else:
                mail.Categories = PROCESSED_CATEGORY

            mail.Save()

        except Exception as e:
            log_global(f"ERROR processing mail: {str(e)}")


if __name__ == "__main__":
    process_mails()