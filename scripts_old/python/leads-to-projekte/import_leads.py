import os
import shutil
from datetime import datetime

# ==========================================
# CONFIG
# ==========================================

LEADS_PATH = r"C:\Users\PV\OneDrive\ENKO GmbH\Leads"
PROJEKTE_PATH = r"C:\Users\PV\OneDrive\ENKO GmbH\Projekte"

GLOBAL_LOG_DIR = r"C:\Users\PV\OneDrive\backend\logs"
GLOBAL_LOG_FILE = os.path.join(GLOBAL_LOG_DIR, "lead_import.log")

SCRIPT_NAME = "lead_import.py"
LEAD_FOLDER = "01_Lead"


# ==========================================
# LOGGING
# ==========================================

def log_global(customer, action):

    os.makedirs(GLOBAL_LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"{timestamp} | {SCRIPT_NAME} | {customer} | {action}\n"

    with open(GLOBAL_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


def log_local(project_path, action):

    log_file = os.path.join(project_path, "log.txt")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"{timestamp} | {SCRIPT_NAME} | {action}\n"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)


# ==========================================
# NAME EXTRACTION
# ==========================================

def extract_name(filename):

    base = os.path.splitext(filename)[0]

    if "_" in base:
        base = base.split("_", 1)[1]

    print("Zeile 58" + base)
    return base.lower()


# ==========================================
# PROJECT SEARCH
# ==========================================

def find_project_folder(name):

    print("searching for:", name)

    matches = []

    for folder in os.listdir(PROJEKTE_PATH):

        parts = folder.lower().split("_", 1)

        if len(parts) < 2:
            continue

        name_part = parts[1]

        name_parts = name_part.split()

        if len(name_parts) < 2:
            continue

        vorname = name_parts[0]
        nachname = name_parts[1]

        print("checking:", vorname, nachname)

        if name == vorname or name == nachname:
            matches.append(folder)

    return matches


# ==========================================
# CREATE PROJECT
# ==========================================

def create_project_folder(name):

    today = datetime.now().strftime("%Y-%m-%d")

    folder_name = f"{today}_{name.capitalize()}"

    project_path = os.path.join(PROJEKTE_PATH, folder_name)

    lead_path = os.path.join(project_path, LEAD_FOLDER)

    os.makedirs(lead_path, exist_ok=True)

    return project_path, folder_name


# ==========================================
# MAIN PROCESS
# ==========================================

def process():

    for root, dirs, files in os.walk(LEADS_PATH):

        for file in files:

            if not file.lower().endswith((".pdf", ".msg")):
                continue

            source = os.path.join(root, file)

            name = extract_name(file)

            matches = find_project_folder(name)

            print("\n-------------------------------------")
            print("Datei:", file)
            print("Extrahierter Name:", name)

            # ==================================
            # EXACTLY ONE MATCH
            # ==================================

            if len(matches) == 1:

                project_folder = matches[0]
                project_path = os.path.join(PROJEKTE_PATH, project_folder)

                print("Projektordner gefunden:", project_folder)
                print(f'"{file}" nach "{project_folder}" verschieben? (y/n)')

                answer = input("> ")

                if answer.lower() == "y":

                    lead_path = os.path.join(project_path, LEAD_FOLDER)
                    os.makedirs(lead_path, exist_ok=True)

                    target = os.path.join(lead_path, file)

                    shutil.copy2(source, target)

                    print("✔ Datei kopiert")

                    log_global(name, f"{file} copied to {project_folder}")
                    log_local(project_path, f"{file} copied to {LEAD_FOLDER}")

                else:

                    print("✖ übersprungen")
                    log_global(name, f"{file} skipped")

            # ==================================
            # MULTIPLE MATCHES
            # ==================================

            elif len(matches) > 1:

                print("Mehrere mögliche Projektordner gefunden:\n")

                for i, folder in enumerate(matches):
                    print(f"{i+1}  {folder}")

                print("\nNummer wählen oder 'n' zum Überspringen")

                answer = input("> ")

                if answer.isdigit():

                    index = int(answer) - 1

                    project_folder = matches[index]
                    project_path = os.path.join(PROJEKTE_PATH, project_folder)

                    lead_path = os.path.join(project_path, LEAD_FOLDER)
                    os.makedirs(lead_path, exist_ok=True)

                    target = os.path.join(lead_path, file)

                    shutil.copy2(source, target)

                    print("✔ Datei kopiert")

                    log_global(name, f"{file} copied to {project_folder}")
                    log_local(project_path, f"{file} copied to {LEAD_FOLDER}")

                else:

                    print("✖ übersprungen")
                    log_global(name, f"{file} skipped (multiple matches)")

            # ==================================
            # NO MATCH
            # ==================================

            else:

                print(f'Kein Projektordner für "{name}" gefunden.')
                print(f'Projektordner für "{name}" erstellen? (y/n)')

                answer = input("> ")

                if answer.lower() == "y":

                    project_path, folder_name = create_project_folder(name)

                    target = os.path.join(project_path, LEAD_FOLDER, file)

                    shutil.copy2(source, target)

                    print("✔ Ordner erstellt und Datei kopiert")

                    log_global(name, f"{file} created project folder {folder_name}")
                    log_local(project_path, f"{file} copied to new project")

                else:

                    print("✖ übersprungen")
                    log_global(name, f"{file} skipped (no folder)")


# ==========================================
# START
# ==========================================

if __name__ == "__main__":
    process()