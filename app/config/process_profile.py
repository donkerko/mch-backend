from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProcessProfile:
    customer_name: str
    process_name: str
    mailbox_name: str
    source_folder: str
    processed_folder: str
    input_dir: Path
    local_log_dir: Path
    excel_path: Path | None = None
    processed_dir: Path | None = None
    error_dir: Path | None = None