from pathlib import Path

from app.config.paths import (
    GLOBAL_LOG_DIR,
    ANFRAGEN_XLSX,
    ANFRAGEN_VOLTALUX_DIR,
    ANFRAGEN_PHOTOVOLTAIKANLAGEAT_DIR,
    ANFRAGEN_PVALARM_DIR,
)
from app.core.constants import SCRIPT_PARSE_ANFRAGEN
from app.core.logging_service import LoggerService
from app.domain.parsers.voltalux_parser import VoltaluxParser
from app.domain.parsers.photovoltaikanlageat_parser import PhotovoltaikanlageATParser
from app.domain.parsers.pvalarm_parser import PVALARMParser
from app.domain.services.parse_anfragen_service import ParseAnfragenService
from app.excel.anfragen_repository import AnfragenRepository


def iter_files(folder: Path, suffix: str):
    folder = Path(folder)
    if not folder.exists():
        return []
    return sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == suffix.lower()])


def main():
    logger = LoggerService(GLOBAL_LOG_DIR, SCRIPT_PARSE_ANFRAGEN)
    repo = AnfragenRepository(ANFRAGEN_XLSX)
    service = ParseAnfragenService(repo, logger)

    voltalux_parser = VoltaluxParser()
    pv_at_parser = PhotovoltaikanlageATParser()
    pvalarm_parser = PVALARMParser()

    logger.log_global("SYSTEM", "Parse-Anfragen gestartet")

    for file_path in iter_files(ANFRAGEN_VOLTALUX_DIR, ".pdf"):
        try:
            lead = voltalux_parser.parse_file(file_path)
            service.import_lead(lead, file_path.name)
        except Exception as e:
            logger.log_global("SYSTEM", f"Fehler Voltalux {file_path.name}: {e}")

    for file_path in iter_files(ANFRAGEN_PHOTOVOLTAIKANLAGEAT_DIR, ".msg"):
        try:
            lead = pv_at_parser.parse_file(file_path)
            service.import_lead(lead, file_path.name)
        except Exception as e:
            logger.log_global("SYSTEM", f"Fehler photovoltaikanlage.at {file_path.name}: {e}")

    for file_path in iter_files(ANFRAGEN_PVALARM_DIR, ".msg"):
        try:
            lead = pvalarm_parser.parse_file(file_path)
            service.import_lead(lead, file_path.name)
        except Exception as e:
            logger.log_global("SYSTEM", f"Fehler PVALARM {file_path.name}: {e}")

    logger.log_global("SYSTEM", "Parse-Anfragen abgeschlossen")


if __name__ == "__main__":
    main()