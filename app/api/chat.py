#this endpoint takes your message, finds relevant info from uploaded documents, 
#generates a response, and sends it back to you

from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint"""
    
    try:
        result = chat_service.chat(
            message=request.message,
            workspace_id=request.workspace_id,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        return ChatResponse(
            response=f"Sorry, I encountered an error: {str(e)}",
            sources=[],
            conversation_id=request.conversation_id or "error"
        )