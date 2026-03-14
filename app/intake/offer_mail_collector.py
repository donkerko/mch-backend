from pathlib import Path

from app.config.process_profile import ProcessProfile
from app.core.logging_service import LoggerService
from app.intake.outlook_client import OutlookClient


class OfferMailCollector:
    def __init__(
        self,
        profile: ProcessProfile,
        logger: LoggerService,
        outlook_client: OutlookClient | None = None,
    ):
        self.profile = profile
        self.logger = logger
        self.outlook = outlook_client or OutlookClient()

        self.profile.input_dir.mkdir(parents=True, exist_ok=True)
        self.profile.local_log_dir.mkdir(parents=True, exist_ok=True)

    def _get_unique_path(self, file_path: Path) -> Path:
        if not file_path.exists():
            return file_path

        counter = 1
        stem = file_path.stem
        suffix = file_path.suffix

        while True:
            candidate = file_path.with_name(f"{stem}_{counter}{suffix}")
            if not candidate.exists():
                return candidate
            counter += 1

    def collect(self) -> list[Path]:
        saved_files: list[Path] = []

        self.logger.log_global(self.profile.customer_name, "collector started")
        self.logger.log_local(self.profile.local_log_dir, "collector started")

        try:
            source_folder = self.outlook.get_folder(
                mailbox_name=self.profile.mailbox_name,
                folder_path=[self.profile.source_folder],
            )

            processed_folder = self.outlook.get_folder(
                mailbox_name=self.profile.mailbox_name,
                folder_path=[self.profile.source_folder, self.profile.processed_folder],
            )

            items = source_folder.Items
            items.Sort("[ReceivedTime]", True)

            for mail in list(items):
                try:
                    if mail.Class != 43:
                        continue

                    saved_any_pdf = False
                    subject = str(getattr(mail, "Subject", "") or "")

                    for attachment in mail.Attachments:
                        filename = str(attachment.FileName)

                        if not filename.lower().endswith(".pdf"):
                            continue

                        target_path = self._get_unique_path(self.profile.input_dir / filename)
                        attachment.SaveAsFile(str(target_path))

                        saved_files.append(target_path)
                        saved_any_pdf = True

                        self.logger.log_global(
                            self.profile.customer_name,
                            f"saved PDF {target_path.name}"
                        )
                        self.logger.log_local(
                            self.profile.local_log_dir,
                            f"saved PDF {target_path.name}"
                        )

                    if saved_any_pdf:
                        mail.Move(processed_folder)

                        self.logger.log_global(
                            self.profile.customer_name,
                            f"moved mail to {self.profile.source_folder}\\{self.profile.processed_folder} | subject: {subject}"
                        )
                        self.logger.log_local(
                            self.profile.local_log_dir,
                            f"moved mail to {self.profile.source_folder}\\{self.profile.processed_folder} | subject: {subject}"
                        )

                except Exception as e:
                    self.logger.log_global(
                        self.profile.customer_name,
                        f"ERROR in collector mail loop: {e}"
                    )
                    self.logger.log_local(
                        self.profile.local_log_dir,
                        f"ERROR in collector mail loop: {e}"
                    )

        except Exception as e:
            self.logger.log_global(
                self.profile.customer_name,
                f"FATAL ERROR in collector: {e}"
            )
            self.logger.log_local(
                self.profile.local_log_dir,
                f"FATAL ERROR in collector: {e}"
            )
            raise

        finally:
            self.logger.log_global(self.profile.customer_name, "collector ended")
            self.logger.log_local(self.profile.local_log_dir, "collector ended")

        return saved_files