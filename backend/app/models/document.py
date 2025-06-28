from pydantic import BaseModel
from typing import List

class DocumentUploadResponse(BaseModel):
    document_id: str
    message: str

class DocumentListResponse(BaseModel):
    documents: List[str]

class DocumentDeleteResponse(BaseModel):
    message: str
