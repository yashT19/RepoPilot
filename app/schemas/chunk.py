from pydantic import BaseModel, Field

from app.schemas.citation import SourceCitation


class CodeChunk(BaseModel):
    repository_id: int
    file_path: str
    language: str
    chunk_index: int
    chunk_id: str
    content: str
    excerpt: str
    start_line: int
    end_line: int
    symbol: str | None = None
    metadata: dict = Field(default_factory=dict)

    def citation(self, score: float | None = None) -> SourceCitation:
        return SourceCitation(
            repository_id=self.repository_id,
            file_path=self.file_path,
            start_line=self.start_line,
            end_line=self.end_line,
            excerpt=self.excerpt,
            score=score,
            symbol=self.symbol,
            language=self.language,
        )