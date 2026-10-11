from fastapi import APIRouter
from app.core.container import container

router=APIRouter(prefix="/chat",
          tags=["Chat"])

@router.post("")
def chat(question:str):
    answer=container.rag_service.answer(question)
    return{
        "question":question,
        "answer":answer
    }