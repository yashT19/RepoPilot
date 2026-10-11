from pathlib import Path

from app.repository_processing.file_filter import FileFilter
from app.schemas.document import CodeDocument


class RepositoryParser:

    def __init__(self):
        self.file_filter = FileFilter()

    def parse_repository(self, repository_path: Path) -> list[CodeDocument]:
        documents = []

        for path in repository_path.rglob("*"):

            # Ignore directories
            if not path.is_file():
                continue

            # Ignore unsupported files
            if not self.file_filter.should_process(path):
                continue

            # Read file content
            content = path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            # Create CodeDocument
            document = CodeDocument(
                file_path=str(path.relative_to(repository_path)),
                language=self._detect_language(path),
                content=content,
                metadata={}
            )

            documents.append(document)

        return documents

    def _detect_language(self, file_path: Path) -> str:

        language_map = {
            ".java": "java",
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".md": "markdown",
            ".xml": "xml",
            ".json": "json",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".properties": "properties",
            ".sql": "sql",
            ".txt": "text",
        }

        return language_map.get(
            file_path.suffix.lower(),
            "text"
        )