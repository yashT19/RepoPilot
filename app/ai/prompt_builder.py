class CodePromptBuilder:

    def build_prompt(
        self,
        question: str,
        retrieved_chunks
    ) -> str:

        context_parts = []

        for result in retrieved_chunks:

            chunk = result["chunk"]

            context_parts.append(
                f"""
File: {chunk.file_path}
Citation: [{chunk.file_path}:{chunk.start_line}-{chunk.end_line}]
Language: {chunk.language}
Chunk: {chunk.chunk_index}

Code:
{chunk.content}
"""
            )

        context = "\n\n".join(context_parts)

        return f"""
You are an AI software engineering assistant.

Answer the user's question using the repository
context provided below.

Rules:
1. Use the repository context as the primary source.
2. Do not invent code or files that are not present.
3. If the context is insufficient, clearly say so.
4. Cite every repository-based claim using [path:start-end].
5. Use only the supplied context and never hallucinate citations.
6. Explain your reasoning clearly.

Repository Context:
{context}

User Question:
{question}

Answer:
"""