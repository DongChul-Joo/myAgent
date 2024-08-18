from typing import Optional
from pydantic import BaseModel, validator
from datetime import datetime

class AuditDto(BaseModel):
    deleted: Optional[bool] = False
    createdAt: Optional[str] = None
    createdBy: Optional[str] = None
    createdByName: Optional[str] = None
    updatedAt: Optional[str] = None
    updatedBy: Optional[str] = None
    updatedByName: Optional[str] = None
    
    class Config:
        use_enum_values = True
  
    @validator('createdAt', 'updatedAt', pre=True, always=True)
    def datetime_to_str(cls, value):
      if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
      return value