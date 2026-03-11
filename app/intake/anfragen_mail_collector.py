from pathlib import Path
from tempfile import NamedTemporaryFile

from app.intake.attachment_name_resolver import AttachmentNameResolver
from app.intake.filename_builder import slug, ensure_unique_path, build_unknown_token


class AnfragenMailCollector:
    def __init__(
        self,
        logger,
        outlook_client,
        mailbox_name: str,
        source_folder,
        classifier,
        allowed_extensions: set[str] | None = None,
    ):
        self.logger = logger
        self.outlook_client = outlook_client
        self.mailbox_name = mailbox_name
        self.source_folder = source_folder
        self.classifier = classifier
        self.allowed_extensions = allowed_extensions or {".pdf", ".msg"}
        self.name_resolver = AttachmentNameResolver()

    def _save_attachment_to_temp(self, attachment) -> Path:
        suffix = Path(attachment.FileName).suffix.lower()

        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_path = Path(tmp.name)

        attachment.SaveAsFile(str(temp_path))
        return temp_path

    def _extract_name(self, attachment) -> tuple[str, str]:
        temp_path = self._save_attachment_to_temp(attachment)

        try:
            return self.name_resolver.resolve_from_attachment_file(temp_path)
        finally:
            try:
                temp_path.unlink(missing_ok=True)
            except Exception:
                pass

    def _build_filename(self, mail, attachment, source_name: str, vorname: str, nachname: str) -> str:
        received = getattr(mail, "ReceivedTime", None)
        if received:
            timestamp = received.Format("%Y-%m-%d_%H%M%S")
        else:
            timestamp = "unknown_time"

        ext = Path(attachment.FileName).suffix.lower()

        if vorname or nachname:
            customer_part = "_".join(filter(None, [slug(nachname), slug(vorname)]))
        else:
            customer_part = f"unbekannt_{build_unknown_token(mail)}"

        source_part = slug(source_name) or "unknown_source"

        return f"{timestamp}_{source_part}_{customer_part}{ext}"

    def _move_mail(self, mail, processed_folder_path: list[str]):
        processed_folder = self.outlook_client.get_folder(self.mailbox_name, processed_folder_path)
        mail.Move(processed_folder)

    def process(self):
        items = self.source_folder.Items
        items.Sort("[ReceivedTime]", True)

        mails = list(items)

        for mail in mails:
            try:
                if getattr(mail, "Class", None) != 43:
                    continue

                classification = self.classifier.classify(mail)

                if classification is None:
                    subject = getattr(mail, "Subject", "") or ""
                    self.logger.log_global("SYSTEM", f"Keine Klassifikation für Mail: {subject}")
                    continue

                classification.target_dir.mkdir(parents=True, exist_ok=True)

                saved_files = []

                for attachment in mail.Attachments:
                    ext = Path(attachment.FileName).suffix.lower()

                    if ext not in self.allowed_extensions:
                        continue

                    vorname, nachname = self._extract_name(attachment)
                    filename = self._build_filename(
                        mail=mail,
                        attachment=attachment,
                        source_name=classification.source_name,
                        vorname=vorname,
                        nachname=nachname,
                    )

                    target_path = ensure_unique_path(classification.target_dir / filename)
                    attachment.SaveAsFile(str(target_path))

                    customer_name = f"{vorname} {nachname}".strip() or "Unbekannt"
                    self.logger.log_global(
                        customer_name,
                        f"Anhang gespeichert [{classification.source_name}]: {target_path}"
                    )

                    saved_files.append(target_path)

                if saved_files:
                    subject = getattr(mail, "Subject", "") or ""
                    self._move_mail(mail, classification.processed_folder_path)
                    self.logger.log_global(
                        "SYSTEM",
                        f"Mail verschoben nach {'/'.join(classification.processed_folder_path)}: {subject}"
                    )

            except Exception as e:
                subject = getattr(mail, "Subject", "") or ""
                self.logger.log_global("SYSTEM", f"Collector-Fehler bei Mail '{subject}': {e}")