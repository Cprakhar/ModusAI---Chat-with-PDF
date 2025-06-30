from pydantic import BaseModel
from typing import List

class DocumentInfo(BaseModel):
    document_id: str
    name: str
    upload_time: str

class DocumentUploadResponse(BaseModel):
    document_id: str
    conversation_id: str
    message: str

class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]

class DocumentDeleteResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str
