from pathlib import Path


class MailClassificationResult:
    def __init__(
        self,
        source_name: str,
        target_dir,
        processed_folder_path: list[str],
    ):
        self.source_name = source_name
        self.target_dir = Path(target_dir)
        self.processed_folder_path = processed_folder_path


class MailClassifier:
    def __init__(self, mailbox_name: str, rules: list[dict]):
        self.mailbox_name = mailbox_name
        self.rules = rules

    def _get_subject(self, mail) -> str:
        return (getattr(mail, "Subject", "") or "").lower()

    def _get_sender_email(self, mail) -> str:
        sender_email = ""

        try:
            sender_email = getattr(mail, "SenderEmailAddress", "") or ""
        except Exception:
            sender_email = ""

        return sender_email.lower()

    def _get_body(self, mail) -> str:
        try:
            body = getattr(mail, "Body", "") or ""
        except Exception:
            body = ""
        return body.lower()

    def _get_attachment_names(self, mail) -> list[str]:
        names = []

        try:
            for attachment in mail.Attachments:
                names.append((attachment.FileName or "").lower())
        except Exception:
            pass

        return names

    def _matches_rule(self, mail, rule: dict) -> bool:
        subject = self._get_subject(mail)
        sender_email = self._get_sender_email(mail)
        body = self._get_body(mail)
        attachment_names = self._get_attachment_names(mail)

        sender_contains = rule.get("sender_contains", [])
        subject_contains = rule.get("subject_contains", [])
        body_contains = rule.get("body_contains", [])
        attachment_name_contains = rule.get("attachment_name_contains", [])
        attachment_extensions = rule.get("attachment_extensions", [])

        if sender_contains and not any(token.lower() in sender_email for token in sender_contains):
            return False

        if subject_contains and not any(token.lower() in subject for token in subject_contains):
            return False

        if body_contains and not any(token.lower() in body for token in body_contains):
            return False

        if attachment_name_contains:
            if not any(
                token.lower() in attachment_name
                for token in attachment_name_contains
                for attachment_name in attachment_names
            ):
                return False

        if attachment_extensions:
            if not any(
                Path(name).suffix.lower() in {ext.lower() for ext in attachment_extensions}
                for name in attachment_names
            ):
                return False

        return True

    def classify(self, mail) -> MailClassificationResult | None:
        for rule in self.rules:
            if self._matches_rule(mail, rule):
                return MailClassificationResult(
                    source_name=rule["source_name"],
                    target_dir=rule["target_dir"],
                    processed_folder_path=rule["processed_folder_path"],
                )

        return None