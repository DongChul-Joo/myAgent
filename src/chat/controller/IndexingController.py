
from fastapi import APIRouter , status , Depends , UploadFile , File
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from ..service import IndexingService
from ..dto.IndexingDto import *

#권한체크 , scheme='Bearer' credentials='token' 형식 반환됨
router = APIRouter(prefix = "/api/indexing")

@router.post("-mv" , response_model=MultiVectorIndexingResponseDto , summary="멀티벡터 색인 등록", description="This endpoint create multi vector index", operation_id="postMultiVectorIndexing")
async def postMultiVectorIndexing(fileList: list[UploadFile] = File(...)):
    response = await IndexingService.postMultiVectorIndexing(fileList)
    return JSONResponse(content=response.dict() , status_code=status.HTTP_200_OK)
  