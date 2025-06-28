from pydantic import BaseModel
from typing import List
from .response import CitationModel

class ChatMessageRequest(BaseModel):
    conversation_id: str
    message: str

class ChatMessageResponse(BaseModel):
    response: str
    citations: List[CitationModel]
    conversation_id: str

class DeepQueryRequest(BaseModel):
    document_id: str
    query: str

class DeepQueryResponse(BaseModel):
    response: str
    citations: List[CitationModel]
