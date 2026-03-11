from app.config.paths import GLOBAL_LOG_DIR, PROJECTS_DIR
from app.core.logging_service import LoggerService
from app.core.constants import SCRIPT_CREATE_PROJECT_FOLDERS
from app.storage.project_folders import ProjectFolderService


def main():
    logger = LoggerService(GLOBAL_LOG_DIR, SCRIPT_CREATE_PROJECT_FOLDERS)
    folder_service = ProjectFolderService(PROJECTS_DIR)

    customer_name = "Max Mustermann"
    project_root = folder_service.create_project_folder_structure(customer_name)

    logger.log_global(customer_name, f"Projektordner erstellt: {project_root}")
    logger.log_local(project_root, "Projektordnerstruktur erstellt")


if __name__ == "__main__":
    main()