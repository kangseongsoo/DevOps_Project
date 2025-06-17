from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# 요청 모델
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class SimpleChatRequest(BaseModel):
    message: str

# 응답 모델
class ChatResponse(BaseModel):
    response: str
    session_id: str
    status: str

class ConversationResponse(BaseModel):
    session_id: str
    conversation: List[Dict[str, Any]]
    status: str

class DeleteResponse(BaseModel):
    session_id: str
    message: str
    status: str

class HealthResponse(BaseModel):
    status: str
    redis: str 