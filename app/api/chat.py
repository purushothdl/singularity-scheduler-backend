from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest
from app.schemas.user import UserInDB
from app.dependencies.auth_dependencies import get_current_user
from app.dependencies.service_dependencies import get_chat_service
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat Agent"])

@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    current_user: UserInDB = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Handles a streaming chat request with the AI agent.

    This endpoint receives the user's input and chat history, then streams
    back the agent's thought process and final response in real-time.
    """
    return StreamingResponse(
        chat_service.stream_agent_response(request, current_user),
        media_type="text/event-stream"
    )