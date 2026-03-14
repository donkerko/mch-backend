import shutil
from pathlib import Path

from app.config.process_profile import ProcessProfile
from app.core.logging_service import LoggerService
from app.domain.parsers.sicherheitssysteme_offer_parser import SicherheitssystemeOfferParser
from app.excel.offer_tracking_repository import OfferTrackingRepository


class OfferParsingService:
    def __init__(
        self,
        profile: ProcessProfile,
        logger: LoggerService,
        parser: SicherheitssystemeOfferParser | None = None,
        repository: OfferTrackingRepository | None = None,
    ):
        self.profile = profile
        self.logger = logger
        self.parser = parser or SicherheitssystemeOfferParser()
        self.repository = repository or OfferTrackingRepository(
            file_path=self.profile.excel_path
        )

        self.profile.input_dir.mkdir(parents=True, exist_ok=True)
        self.profile.processed_dir.mkdir(parents=True, exist_ok=True)
        self.profile.error_dir.mkdir(parents=True, exist_ok=True)
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

    def _move_file(self, source_path: Path, target_dir: Path) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = self._get_unique_path(target_dir / source_path.name)
        shutil.move(str(source_path), str(target_path))
        return target_path

    def process_all(
        self,
        max_files: int | None = None,
        filenames: list[str] | None = None,
    ) -> None:
        processed_count = 0
        error_count = 0
        duplicate_count = 0

        self.logger.log_global(self.profile.customer_name, "offer parser started")
        self.logger.log_local(self.profile.local_log_dir, "offer parser started")

        try:
            existing_offer_numbers = self.repository.get_existing_offer_numbers()

            if filenames:
                pdf_files = [
                    self.profile.input_dir / name
                    for name in filenames
                    if (self.profile.input_dir / name).exists()
                ]

                self.logger.log_global(
                    self.profile.customer_name,
                    f"test mode specific files: {', '.join(filenames)}"
                )
                self.logger.log_local(
                    self.profile.local_log_dir,
                    f"test mode specific files: {', '.join(filenames)}"
                )
            else:
                pdf_files = sorted(self.profile.input_dir.glob("*.pdf"))

            if max_files is not None:
                pdf_files = pdf_files[:max_files]
                self.logger.log_global(
                    self.profile.customer_name,
                    f"test mode active | max_files={max_files}"
                )
                self.logger.log_local(
                    self.profile.local_log_dir,
                    f"test mode active | max_files={max_files}"
                )

            for pdf_path in pdf_files:
                try:
                    offer = self.parser.parse(pdf_path)

                    if not offer.angebot_nr:
                        error_path = self._move_file(pdf_path, self.profile.error_dir)
                        error_count += 1

                        self.logger.log_global(
                            self.profile.customer_name,
                            f"ERROR missing offer number, moved to Fehler: {error_path.name}"
                        )
                        self.logger.log_local(
                            self.profile.local_log_dir,
                            f"ERROR missing offer number, moved to Fehler: {error_path.name}"
                        )
                        continue

                    if offer.angebot_nr.strip().lower() in existing_offer_numbers:
                        processed_path = self._move_file(pdf_path, self.profile.processed_dir)
                        duplicate_count += 1

                        self.logger.log_global(
                            self.profile.customer_name,
                            f"duplicate offer skipped {offer.angebot_nr} | moved to Verarbeitet: {processed_path.name}"
                        )
                        self.logger.log_local(
                            self.profile.local_log_dir,
                            f"duplicate offer skipped {offer.angebot_nr} | moved to Verarbeitet: {processed_path.name}"
                        )
                        continue

                    processed_path = self._move_file(pdf_path, self.profile.processed_dir)
                    offer.angebot_pfad = str(processed_path)

                    self.repository.append_offer(offer)
                    existing_offer_numbers.add(offer.angebot_nr.strip().lower())
                    processed_count += 1

                    self.logger.log_global(
                        self.profile.customer_name,
                        f"offer added to excel {offer.angebot_nr}"
                    )
                    self.logger.log_local(
                        self.profile.local_log_dir,
                        f"offer added to excel {offer.angebot_nr}"
                    )

                except Exception as e:
                    error_count += 1

                    try:
                        error_path = self._move_file(pdf_path, self.profile.error_dir)
                        filename_info = error_path.name
                    except Exception:
                        filename_info = pdf_path.name

                    self.logger.log_global(
                        self.profile.customer_name,
                        f"ERROR parsing {filename_info}: {e}"
                    )
                    self.logger.log_local(
                        self.profile.local_log_dir,
                        f"ERROR parsing {filename_info}: {e}"
                    )

        except Exception as e:
            self.logger.log_global(
                self.profile.customer_name,
                f"FATAL ERROR in offer parser service: {e}"
            )
            self.logger.log_local(
                self.profile.local_log_dir,
                f"FATAL ERROR in offer parser service: {e}"
            )
            raise

        finally:
            if error_count == 0:
                end_message = (
                    f"offer parser finished successfully | processed={processed_count} | "
                    f"duplicates={duplicate_count} | errors={error_count}"
                )
            else:
                end_message = (
                    f"offer parser finished with errors | processed={processed_count} | "
                    f"duplicates={duplicate_count} | errors={error_count}"
                )

            self.logger.log_global(self.profile.customer_name, end_message)
            self.logger.log_local(self.profile.local_log_dir, end_message)
        return {
            "processed": processed_count,
            "duplicates": duplicate_count,
            "errors": error_count,
        }