
from fastapi import APIRouter , status , Depends , UploadFile , File
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from ..service import IndexingService
from ..dto.IndexingDto import *

#권한체크 , scheme='Bearer' credentials='token' 형식 반환됨
router = APIRouter(prefix = "/api/indexing")

@router.post("-pd" , response_model=ParentDocumentIndexingResponseDto , summary="부모문서 색인 등록", description="This endpoint create parent document index", operation_id="postParentDocumentIndexing")
async def postParentDocumentIndexing(fileList: list[UploadFile] = File(...)):
    response = await IndexingService.postParentDocumentIndexing(fileList)
    return JSONResponse(content=response.dict() , status_code=status.HTTP_200_OK)
  