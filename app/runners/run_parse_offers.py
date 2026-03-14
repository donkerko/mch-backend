from app.config.customers.sicherheitssysteme_voecklabruck import SICHERHEITSSYSTEME_OFFERS
from app.config.paths import GLOBAL_LOG_DIR
from app.core.logging_service import LoggerService
from app.domain.services.offer_parsing_service import OfferParsingService


TEST_MODE = False
TEST_MAX_FILES = 1
TEST_FILENAMES: list[str] | None = None
# Beispiel:
# TEST_FILENAMES = ["An-VB-100_2025.pdf"]


def main():
    logger = LoggerService(
        global_log_dir=GLOBAL_LOG_DIR,
        script_name="run_parse_offers",
    )

    try:
        logger.log_global(
            SICHERHEITSSYSTEME_OFFERS.customer_name,
            "runner started"
        )

        service = OfferParsingService(
            profile=SICHERHEITSSYSTEME_OFFERS,
            logger=logger,
        )

        if TEST_MODE:
            if TEST_FILENAMES:
                logger.log_global(
                    SICHERHEITSSYSTEME_OFFERS.customer_name,
                    f"TEST MODE active | filenames={', '.join(TEST_FILENAMES)}"
                )
                logger.log_local(
                    SICHERHEITSSYSTEME_OFFERS.local_log_dir,
                    f"TEST MODE active | filenames={', '.join(TEST_FILENAMES)}"
                )

                result = service.process_all(filenames=TEST_FILENAMES)

            else:
                logger.log_global(
                    SICHERHEITSSYSTEME_OFFERS.customer_name,
                    f"TEST MODE active | max_files={TEST_MAX_FILES}"
                )
                logger.log_local(
                    SICHERHEITSSYSTEME_OFFERS.local_log_dir,
                    f"TEST MODE active | max_files={TEST_MAX_FILES}"
                )

                result = service.process_all(max_files=TEST_MAX_FILES)

        else:
            result = service.process_all()

        if result["errors"] == 0:
            logger.log_global(
                SICHERHEITSSYSTEME_OFFERS.customer_name,
                (
                    f"runner finished successfully | "
                    f"processed={result['processed']} | "
                    f"duplicates={result['duplicates']} | "
                    f"errors={result['errors']}"
                )
            )
            logger.log_local(
                SICHERHEITSSYSTEME_OFFERS.local_log_dir,
                (
                    f"runner finished successfully | "
                    f"processed={result['processed']} | "
                    f"duplicates={result['duplicates']} | "
                    f"errors={result['errors']}"
                )
            )
        else:
            logger.log_global(
                SICHERHEITSSYSTEME_OFFERS.customer_name,
                (
                    f"runner finished with errors | "
                    f"processed={result['processed']} | "
                    f"duplicates={result['duplicates']} | "
                    f"errors={result['errors']}"
                )
            )
            logger.log_local(
                SICHERHEITSSYSTEME_OFFERS.local_log_dir,
                (
                    f"runner finished with errors | "
                    f"processed={result['processed']} | "
                    f"duplicates={result['duplicates']} | "
                    f"errors={result['errors']}"
                )
            )

    except Exception as e:
        logger.log_global(
            SICHERHEITSSYSTEME_OFFERS.customer_name,
            f"FATAL ERROR in run_parse_offers: {e}"
        )
        logger.log_local(
            SICHERHEITSSYSTEME_OFFERS.local_log_dir,
            f"FATAL ERROR in run_parse_offers: {e}"
        )
        raise


if __name__ == "__main__":
    main()