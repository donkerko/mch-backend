import os
import hashlib
from datetime import datetime

# ==========================
# CONFIG
# ==========================

ANFRAGEN_PATH = r"C:\Users\PV\OneDrive\ENKO GmbH\Anfragen"

GLOBAL_LOG_DIR = r"C:\Users\PV\OneDrive\backend\logs"
GLOBAL_LOG_FILE = os.path.join(GLOBAL_LOG_DIR, "duplicate_cleanup.log")

SCRIPT_NAME = "duplicate_cleanup.py"


# ==========================
# LOGGING
# ==========================

def log_global(action):

    os.makedirs(GLOBAL_LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"{timestamp} | {SCRIPT_NAME} | {action}\n"

    with open(GLOBAL_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


# ==========================
# HASH FUNCTION
# ==========================

def file_hash(path):

    sha256 = hashlib.sha256()

    with open(path, "rb") as f:

        while chunk := f.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


# ==========================
# DUPLICATE CHECK
# ==========================

def find_duplicates():

    hashes = {}

    for root, dirs, files in os.walk(ANFRAGEN_PATH):

        for file in files:

            if not file.endswith((".pdf", ".msg")):
                continue

            path = os.path.join(root, file)

            try:

                h = file_hash(path)

            except Exception as e:

                print("Fehler beim Lesen:", path)
                continue

            if h not in hashes:

                hashes[h] = path

            else:

                original = hashes[h]

                print("\n-----------------------------------")
                print("Duplikat gefunden")
                print("Original :", original)
                print("Duplikat :", path)
                print("Duplikat löschen? (y/n)")

                answer = input("> ")

                if answer.lower() == "y":

                    os.remove(path)

                    print("✔ gelöscht")

                    log_global(f"deleted duplicate {path} (original {original})")

                else:

                    print("✖ behalten")

                    log_global(f"kept duplicate {path}")


# ==========================
# START
# ==========================

if __name__ == "__main__":

    find_duplicates()