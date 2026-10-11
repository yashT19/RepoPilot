from pathlib import Path, PurePath, PureWindowsPath

from pydantic import BaseModel, Field, field_validator


class SourceCitation(BaseModel):
    repository_id: int
    file_path: str
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    excerpt: str
    score: float | None = None
    retrieval_source: str = "faiss"
    symbol: str | None = None
    language: str | None = None

    @field_validator("file_path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        path = value.replace("\\", "/")
        parsed = PurePath(path)
        if (
            not path
            or path.startswith("/")
            or path.startswith("\\")
            or PureWindowsPath(path).drive
            or any(part == ".." for part in parsed.parts)
        ):
            raise ValueError("file_path must be a relative repository path")
        return path

    @field_validator("end_line")
    @classmethod
    def validate_line_order(cls, value: int, info) -> int:
        start_line = info.data.get("start_line")
        if start_line is not None and value < start_line:
            raise ValueError("end_line must be greater than or equal to start_line")
        return value

    def validate_against(self, repository_root: Path) -> "SourceCitation":
        root = repository_root.resolve()
        source_path = (root / self.file_path).resolve()
        try:
            source_path.relative_to(root)
        except ValueError as exc:
            raise ValueError("citation path escapes the repository") from exc

        if not source_path.is_file():
            raise ValueError(f"citation file does not exist: {self.file_path}")

        lines = source_path.read_text(encoding="utf-8", errors="ignore").splitlines(
            keepends=True
        )
        if self.end_line > len(lines):
            raise ValueError("citation line range is outside the source file")

        cited_text = "".join(lines[self.start_line - 1 : self.end_line])
        if self.excerpt not in cited_text:
            raise ValueError("citation excerpt does not match the source file")
        return self