from pathlib import Path


class FileFilter:

    IGNORED_DIRECTORIES = {
        ".git",
        ".idea",
        ".vscode",
        "node_modules",
        "target",
        "build",
        "__pycache__",
        ".pytest_cache",
        "venv",
        ".venv"
    }

    SUPPORTED_EXTENSIONS = {
        ".java",
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".md",
        ".txt",
        ".xml",
        ".yml",
        ".yaml",
        ".properties",
        ".json",
        ".sql",
        ".dockerfile"
    }

    def should_process(self, file_path: Path) -> bool:

        if any(
            part in self.IGNORED_DIRECTORIES
            for part in file_path.parts
    ):
           return False

        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return False

        return True