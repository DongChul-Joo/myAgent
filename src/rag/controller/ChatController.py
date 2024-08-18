from fastapi import APIRouter , status , Depends , UploadFile , File
from fastapi.responses import JSONResponse

from ..service import ChatService
from ..dto.ChatDto import *

#권한체크 , scheme='Bearer' credentials='token' 형식 반환됨
router = APIRouter(prefix = "/api/chat")

@router.post("" , summary="chat completion", description="This endpoint send message to llm and response llm generation message", operation_id="postChat")
async def postChat(req : ChatRequestDto):
    response = await ChatService.postChat(req)
    return JSONResponse(content=response.dict() , status_code=status.HTTP_200_OK)