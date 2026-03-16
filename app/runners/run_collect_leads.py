from app.config.paths import (
    GLOBAL_LOG_DIR,
    LEADS_VOLTALUX_DIR,
    LEADS_PHOTOVOLTAIKANLAGEAT_DIR,
    LEADS_PVALARM_DIR,
)
from app.core.logging_service import LoggerService
from app.intake.outlook_client import OutlookClient
from app.intake.mail_classifier import MailClassifier
from app.intake.leads_mail_collector import LeadsMailCollector

SCRIPT_NAME = "run_collect_leads"


def main():
    logger = LoggerService(GLOBAL_LOG_DIR, SCRIPT_NAME)
    outlook = OutlookClient()

    mailbox_name = "huetter@enko.at"
    inbox_folder_path = ["Posteingang"]

    rules = [
        {
            "source_name": "photovoltaikanlageAT",
            "target_dir": LEADS_PHOTOVOLTAIKANLAGEAT_DIR,
            "processed_folder_path": ["Posteingang", "Gespeichert"],
            "sender_contains": ["kontakt@leadmail.no"],
            "subject_contains": ["photovoltaikanlage.at"],
            "attachment_extensions": [".msg"],
        },
        {
            "source_name": "Voltalux",
            "target_dir": LEADS_VOLTALUX_DIR,
            "processed_folder_path": ["Posteingang", "Gespeichert"],
            "subject_contains": ["voltalux"],
            "attachment_extensions": [".pdf", ".msg"],
        },
        {
            "source_name": "PVALARM",
            "target_dir": LEADS_PVALARM_DIR,
            "processed_folder_path": ["Posteingang", "Gespeichert"],
            "body_contains": ["Anfragealarm"],
            "attachment_extensions": [".msg"],
        },
    ]

    classifier = MailClassifier(mailbox_name=mailbox_name, rules=rules)

    source_folder = outlook.get_folder(mailbox_name, inbox_folder_path)

    collector = LeadsMailCollector(
        logger=logger,
        outlook_client=outlook,
        mailbox_name=mailbox_name,
        source_folder=source_folder,
        classifier=classifier,
    )

    logger.log_global("SYSTEM", "Collect-Leads gestartet")
    collector.process()
    logger.log_global("SYSTEM", "Collect-Leads abgeschlossen")


if __name__ == "__main__":
    main()