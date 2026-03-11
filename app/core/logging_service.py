from datetime import datetime
from pathlib import Path


class LoggerService:
    def __init__(self, global_log_dir: Path, script_name: str):
        self.global_log_dir = Path(global_log_dir)
        self.script_name = script_name
        self.global_log_dir.mkdir(parents=True, exist_ok=True)

    def log_global(self, customer_name: str, action: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = self.global_log_dir / f"{self.script_name}.log"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | {self.script_name} | {customer_name} | {action}\n")

    def log_local(self, project_path: Path, action: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        project_path = Path(project_path)
        project_path.mkdir(parents=True, exist_ok=True)

        log_file = project_path / "log.txt"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | {self.script_name} | {action}\n")