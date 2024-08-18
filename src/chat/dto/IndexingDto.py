from typing import Optional , List

from pydantic import BaseModel, Field, validator
from fastapi import UploadFile

from ...common.dto.AuditDto import AuditDto

class FileInfo:
    uuid: Optional[str] = Field(None, title="파일 아이디", description="UUID 형식의 색인 아이디를 나타냅니다.")
    fullName: Optional[str] = Field(None, title="파일명 및 확장자", description="파일명과 확장자를 포함한 전체 이름입니다.")
    name: Optional[str] = Field(None, title="파일명", description="파일의 이름입니다 (확장자 제외).")
    extension: Optional[str] = Field(None, title="확장자", description="파일의 확장자를 나타냅니다.")
    
class MultiVectorIndexingResponseDto(AuditDto):
    uuid: Optional[str] = Field(None, title="색인 아이디", description="UUID 형식의 색인 아이디를 나타냅니다.")
    fileInfoList = list[FileInfo]