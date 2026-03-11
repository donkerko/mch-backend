from pathlib import Path
from app.config.settings import DEFAULT_PROJECT_SUBFOLDERS
from app.core.file_utils import ensure_dir
from app.core.name_normalizer import normalize_text


class ProjectFolderService:
    def __init__(self, base_projects_dir: Path):
        self.base_projects_dir = Path(base_projects_dir)

    def build_project_folder_name(self, customer_name: str) -> str:
        return normalize_text(customer_name)

    def create_project_folder_structure(self, customer_name: str) -> Path:
        folder_name = self.build_project_folder_name(customer_name)
        project_root = ensure_dir(self.base_projects_dir / folder_name)

        for subfolder in DEFAULT_PROJECT_SUBFOLDERS:
            ensure_dir(project_root / subfolder)

        return project_root