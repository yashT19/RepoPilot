from app.schemas.document import CodeDocument
from app.schemas.chunk import CodeChunk

class CodeChunker:
    def __init__(self,
                 chunk_size:int=1500,
                 chunk_overlap:int=200):
        if chunk_overlap>= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size=chunk_size
        self.chunk_overlap=chunk_overlap
        

    def chunk_document(
        self,
        document: CodeDocument,
        repository_id: int = 0,
    )-> list[CodeChunk]:
        content=document.content
        if not content.strip():
            return []
        chunks=[]
        start=0
        chunk_index=0
        while start< len(content):
            end=min(start+self.chunk_size, len(content))
            if end< len(content):
                newline_position = content.rfind("\n", start, end)
                if newline_position>start:
                    end=newline_position+1
            chunk_content=content[start:end]
            if chunk_content.strip():
                chunks.append(CodeChunk(
                    repository_id=repository_id,
                    file_path=document.file_path,
                    language=document.language,
                    chunk_index=chunk_index,
                    chunk_id=f"{repository_id}:{document.file_path}:{chunk_index}",
                    content=chunk_content,
                    excerpt=chunk_content,
                    start_line=content.count("\n", 0, start) + 1,
                    end_line=content.count("\n", 0, max(start, end - 1)) + 1,
                    symbol=document.metadata.get("symbol"),
                    metadata=document.metadata))
                chunk_index+=1

            if end>=len(content):
                break
            next_start=end-self.chunk_overlap
            if next_start<=start:
                next_start=end
            start=   next_start     

        return chunks            