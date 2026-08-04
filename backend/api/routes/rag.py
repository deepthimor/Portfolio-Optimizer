from fastapi import APIRouter, HTTPException

from backend.schemas.portfolio import RagAskRequest, RagAskResponse
from backend.services.rag_retrieval import ask_rag_question

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/ask", response_model=RagAskResponse)
def ask_rag(request: RagAskRequest):
    try:
        return ask_rag_question(request.question)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))