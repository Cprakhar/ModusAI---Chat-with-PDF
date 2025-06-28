from pydantic import BaseModel
from typing import List, Optional

class CitationModel(BaseModel):
    document_id: str
    page: int
    chunk_id: Optional[str]
    snippet: Optional[str]
    confidence: Optional[float]
    citation_type: str
    formatted: str

class MessageModel(BaseModel):
    role: str
    content: str
    timestamp: str

class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    history: List[MessageModel]

class ConversationDeleteResponse(BaseModel):
    message: str

class HealthCheckResponse(BaseModel):
    status: str
