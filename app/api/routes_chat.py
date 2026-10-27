# pyrefly: ignore[missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore[missing-import]
from sqlalchemy.orm import Session
from app.db.session import get_db
from src.core.llm import LLMClient   # existing LLM fail‑over client
from schemas.contracts import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Simple chat endpoint that forwards the user query to the LLM client.
    The LLM client already implements the multi‑provider fail‑over logic
    (Gemini → Groq → OpenRouter). Returns the LLM’s answer verbatim.
    """
    try:
        # The LLMClient exposes a `complete` method that takes a prompt.
        answer = LLMClient().complete(request.prompt)
        return ChatResponse(success=True, answer=answer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
