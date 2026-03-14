from app.config.customers.sicherheitssysteme_voecklabruck import SICHERHEITSSYSTEME_OFFERS
from app.config.paths import GLOBAL_LOG_DIR
from app.core.logging_service import LoggerService
from app.intake.offer_mail_collector import OfferMailCollector


def main():
    logger = LoggerService(
        global_log_dir=GLOBAL_LOG_DIR,
        script_name="run_collect_offers",
    )

    try:
        logger.log_global(
            SICHERHEITSSYSTEME_OFFERS.customer_name,
            "runner started"
        )

        collector = OfferMailCollector(
            profile=SICHERHEITSSYSTEME_OFFERS,
            logger=logger,
        )

        collector.collect()

        logger.log_global(
            SICHERHEITSSYSTEME_OFFERS.customer_name,
            "runner finished successfully"
        )

    except Exception as e:
        logger.log_global(
            SICHERHEITSSYSTEME_OFFERS.customer_name,
            f"FATAL ERROR in run_collect_offers: {e}"
        )
        logger.log_local(
            SICHERHEITSSYSTEME_OFFERS.local_log_dir,
            f"FATAL ERROR in run_collect_offers: {e}"
        )
        raise


if __name__ == "__main__":
    main()