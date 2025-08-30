from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_grok(request: ChatRequest):
    try:
        message = request.message
        crop = request.context.get("crop", "unknown") if request.context else "unknown"
        language = request.language

        # Mock response (replace with actual model logic if available)
        response_text = (
            f"Based on your query '{message}', I recommend checking soil health and consulting local agricultural guidelines. "
            f"For {crop}, consider organic fertilizers. Relevant government schemes: PM-KISAN, National Mission for Sustainable Agriculture."
        )

        return {
            "response": response_text,
            "language": language
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")