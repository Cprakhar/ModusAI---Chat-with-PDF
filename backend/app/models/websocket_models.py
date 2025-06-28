from pydantic import BaseModel
from typing import Optional, List, Any

class WSChatTokenMessage(BaseModel):
    token: str
    type: str = "token"

class WSCitationsMessage(BaseModel):
    citations: List[Any]  # Should match your CitationModel
    conversation_id: str
    done: bool = True
    type: str = "citations"

class WSErrorMessage(BaseModel):
    error: str
    type: str = "error"

class WSStreamDoneMessage(BaseModel):
    done: bool = True
    type: str = "done"
