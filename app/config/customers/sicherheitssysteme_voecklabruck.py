from app.config.paths import get_customer_root
from app.config.process_profile import ProcessProfile

CUSTOMER_NAME = "Sicherheitssysteme Vöcklabruck GmbH"
BASE_DIR = get_customer_root(CUSTOMER_NAME)
OFFERS_DIR = BASE_DIR / "Angebote"

SICHERHEITSSYSTEME_OFFERS = ProcessProfile(
    customer_name=CUSTOMER_NAME,
    process_name="offers",
    mailbox_name="huetter@mchvertrieb.at",
    source_folder="Sicherheitssysteme",
    processed_folder="Gespeichert",
    input_dir=OFFERS_DIR / "Eingang",
    processed_dir=OFFERS_DIR / "Verarbeitet",
    error_dir=OFFERS_DIR / "Fehler",
    excel_path=BASE_DIR / "SYSS Angebote - Kontaktliste.xlsx",
    local_log_dir=BASE_DIR / "logs",
)