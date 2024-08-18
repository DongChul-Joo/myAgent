from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

class Sort(BaseModel):
  property: str
  sorted: bool
  def isEmpty(self)-> bool: property is None
  def isUnsorted(self)-> bool: self.isEmpty() or not self.sorted

class Pageable(BaseModel):
  page: int
  size: int

class PageableResponse(BaseModel):
  sort: Optional[Sort] = None
  pageNumber: int
  pageSize: int
  def paged(): bool = True
  def getOffset(self)->int : self.pageNumber * self.pageSize
  def isUnpaged(self): bool = not self.paged

class Page(BaseModel, Generic[T]):
  content: List[T] = Field(default_factory=list)
  pageble: Optional[PageableResponse] = None
  totalElements: int
  totalPages: int
  size: int
  number: int
  sort: Sort
  def isEmpty(self) -> bool: self.content.empty()
  def isLast(self) -> bool: self.number == (self.totalPages - 1)
  def isFirst(self) -> bool: self.number == 0
  def getNumberOfElements(self) -> int: self.content.size()



