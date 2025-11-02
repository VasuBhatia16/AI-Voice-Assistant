from fastapi import APIRouter, HTTPException
from app.models.schema import ChatRequest, ChatResponse
from app.core.llm_client import LLMClient

router = APIRouter()
llm_client = LLMClient()


@router.post('/reply', response_model=ChatResponse)
async def reply_to_message(req: ChatRequest):
    try:
        user_message = req.prompt
        session_id = req.session_id
        ai_reply = await llm_client.get_reply(user_message=user_message, session_id=session_id)
        res = ChatResponse(response=ai_reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exception: {str(e)} || reply_to_message")
    return res