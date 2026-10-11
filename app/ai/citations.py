from app.schemas.citation import SourceCitation


def citations_from_results(results) -> list[SourceCitation]:
    citations = []
    seen = set()
    for result in results:
        citation = SourceCitation.model_validate(
            result.get("citation") or result["chunk"].citation(result.get("score"))
        )
        key = (citation.file_path, citation.start_line, citation.end_line)
        if key not in seen:
            citations.append(citation)
            seen.add(key)
    return citations