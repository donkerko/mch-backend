from pathlib import Path

BACKEND_ROOT = Path(r"C:\Users\PV\OneDrive\backend")
GLOBAL_LOG_DIR = BACKEND_ROOT / "logs"

ENKO_ROOT = Path(r"C:\Users\PV\OneDrive\ENKO GmbH")

ANFRAGEN_DIR = ENKO_ROOT / "Anfragen"
ANFRAGEN_XLSX = ANFRAGEN_DIR / "Anfragen.xlsx"

ANFRAGEN_VOLTALUX_DIR = ANFRAGEN_DIR / "Voltalux"
ANFRAGEN_PHOTOVOLTAIKANLAGEAT_DIR = ANFRAGEN_DIR / "photovoltaikAT"
ANFRAGEN_PVALARM_DIR = ANFRAGEN_DIR / "PVALARM"

CRM_XLSX = ENKO_ROOT / "Projektübersicht.xlsx"
ANGEBOTE_ZU_ERSTELLEN_XLSX = ENKO_ROOT / "Angebote zu erstellen.xlsx"
KALKULATION_TEMPLATE_XLSX = ENKO_ROOT / "Vorlagen" / "MCH_Kalkulation_Vorlage.xlsx"

PROJECTS_DIR = ENKO_ROOT / "Projekte"