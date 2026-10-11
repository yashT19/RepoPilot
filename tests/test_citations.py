from pathlib import Path
import os

import pytest

for name, value in {
    "APP_NAME": "test",
    "API_V1_PREFIX": "/api/v1",
    "HOST": "127.0.0.1",
    "PORT": "8000",
    "DATABASE_URL": "sqlite://",
    "GROQ_API_KEY": "test",
    "GROQ_MODEL": "test",
    "STORAGE_ROOT": "storage",
    "LANGSMITH_TRACING": "false",
    "LANGSMITH_API_KEY": "test",
    "LANGSMITH_PROJECT": "test",
}.items():
    os.environ.setdefault(name, value)

from app.ai.citations import citations_from_results
from app.agents.code_analysis_agent import CodeAnalysisAgent
from app.agents.code_modification_agent import CodeModificationAgent
from app.agents.code_review_agent import CodeReviewAgent
from app.agents.testing_agent import TestingAgent as CodeTestingAgent
from app.repository_processing.chunker import CodeChunker
from app.schemas.citation import SourceCitation
from app.schemas.document import CodeDocument


class FakeRetriever:
    def __init__(self, results):
        self.results = results

    def retrieve(self, **_kwargs):
        return self.results


class FakeLLM:
    def __init__(self, response):
        self.response = response
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return self.response


def make_result():
    chunk = CodeChunker(chunk_size=100, chunk_overlap=0).chunk_document(
        CodeDocument(file_path="module.py", language="python", content="value = 1\n"),
        repository_id=42,
    )[0]
    return {"chunk": chunk, "score": 0.9}


def test_chunk_contains_repository_and_line_metadata(tmp_path: Path):
    source = "first\nsecond\nthird\n"
    (tmp_path / "module.py").write_text(source, encoding="utf-8")

    chunks = CodeChunker(chunk_size=13, chunk_overlap=0).chunk_document(
        CodeDocument(file_path="module.py", language="python", content=source),
        repository_id=42,
    )

    assert chunks[0].repository_id == 42
    assert chunks[0].chunk_id == "42:module.py:0"
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 2
    assert chunks[0].excerpt == chunks[0].content


def test_retrieval_citations_preserve_score_and_source():
    chunk = CodeChunker(chunk_size=100, chunk_overlap=0).chunk_document(
        CodeDocument(file_path="module.py", language="python", content="value = 1\n"),
        repository_id=42,
    )[0]

    results = citations_from_results([{"chunk": chunk, "score": 0.75}])

    assert results[0].file_path == "module.py"
    assert results[0].score == 0.75
    assert results[0].retrieval_source == "faiss"


@pytest.mark.parametrize("file_path", ["C:/repo/module.py", "/repo/module.py", "../module.py"])
def test_citation_rejects_unsafe_paths(file_path: str):
    with pytest.raises(ValueError):
        SourceCitation(
            repository_id=42,
            file_path=file_path,
            start_line=1,
            end_line=1,
            excerpt="value = 1\n",
        )


def test_citation_rejects_bad_range_and_excerpt(tmp_path: Path):
    (tmp_path / "module.py").write_text("value = 1\n", encoding="utf-8")

    with pytest.raises(ValueError):
        SourceCitation(
            repository_id=42,
            file_path="module.py",
            start_line=2,
            end_line=1,
            excerpt="value = 1\n",
        )

    citation = SourceCitation(
        repository_id=42,
        file_path="module.py",
        start_line=1,
        end_line=1,
        excerpt="not source code",
    )
    with pytest.raises(ValueError):
        citation.validate_against(tmp_path)

    missing = SourceCitation(
        repository_id=42,
        file_path="missing.py",
        start_line=1,
        end_line=1,
        excerpt="value = 1\n",
    )
    with pytest.raises(ValueError):
        missing.validate_against(tmp_path)


@pytest.mark.parametrize(
    ("agent_type", "response", "method"),
    [
        (CodeAnalysisAgent, "analysis [module.py:1-1]", "analyze"),
        (CodeReviewAgent, '{"summary":"ok","issues":[]}', "review"),
        (CodeTestingAgent, '{"summary":"ok","test_cases":[]}', "generate_tests"),
        (
            CodeModificationAgent,
            '{"summary":"change","files":[]}',
            "propose_change",
        ),
    ],
)
def test_agents_return_grounded_citations(agent_type, response, method):
    llm = FakeLLM(response)
    agent = agent_type(llm, FakeRetriever([make_result()]))

    result = getattr(agent, method)("inspect module", 42)

    assert result["citations"][0].file_path == "module.py"
    assert result["citations"][0].start_line == 1
    assert "[module.py:1-1]" in llm.prompts[0]