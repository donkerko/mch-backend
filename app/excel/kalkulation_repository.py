from pathlib import Path
from app.core.file_utils import copy_file


class KalkulationRepository:
    def __init__(self, template_path: Path):
        self.template_path = Path(template_path)

    def create_from_template(self, target_path: Path, overwrite: bool = False) -> Path:
        return copy_file(self.template_path, target_path, overwrite=overwrite)