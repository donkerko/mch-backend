from pathlib import Path
import os


def get_onedrive_root() -> Path:
    onedrive = os.environ.get("OneDrive")
    if not onedrive:
        raise RuntimeError("OneDrive environment variable not found.")
    return Path(onedrive)


ONEDRIVE_ROOT = get_onedrive_root()

BACKEND_ROOT = ONEDRIVE_ROOT / "backend"
GLOBAL_LOG_DIR = BACKEND_ROOT / "logs"

ENKO_ROOT = ONEDRIVE_ROOT / "ENKO GmbH"

LEADS_DIR = ENKO_ROOT / "Leads"
LEADS_XLSX = LEADS_DIR / "Leads.xlsx"

LEADS_VOLTALUX_DIR = LEADS_DIR / "Voltalux"
LEADS_PHOTOVOLTAIKANLAGEAT_DIR = LEADS_DIR / "photovoltaikAT"
LEADS_PVALARM_DIR = LEADS_DIR / "PVALARM"

CRM_XLSX = ENKO_ROOT / "Projektübersicht.xlsx"
ANGEBOTE_ZU_ERSTELLEN_XLSX = ENKO_ROOT / "Angebote zu erstellen.xlsx"
KALKULATION_TEMPLATE_XLSX = ENKO_ROOT / "Vorlagen" / "MCH_Kalkulation_Vorlage.xlsx"

PROJECTS_DIR = ENKO_ROOT / "Projekte"


def get_customer_root(customer_folder_name: str) -> Path:
    return ONEDRIVE_ROOT / customer_folder_name