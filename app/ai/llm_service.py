from langsmith import traceable
from langchain_groq import ChatGroq

from app.config.settings import settings

class LLMService:
 def __init__(self):

    api_key = settings.GROQ_API_KEY
    model = settings.GROQ_MODEL

    if not api_key:
        raise ValueError(
            "GROQ API key not configured"
        )

    self.llm = ChatGroq(
        model=model,
        api_key=api_key,
        temperature=0
    )

# ==================================================
# Generate LLM Response
# ==================================================

 @traceable(
    name="LLM Generate",
    run_type="llm"
)
 def generate(
    self,
    prompt: str
) -> str:

    response = self.llm.invoke(
        prompt
    )

    return response.content

