from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime

# 사용자 인증 모델
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

# 챗봇 요청 모델 (사용자 인증 추가)
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
    mariadb: str

# 세션 관리 모델
class ChatSessionCreate(BaseModel):
    title: Optional[str] = "새로운 대화"

class ChatSessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

# 벡터 컬렉션 모델
class VectorCollectionCreate(BaseModel):
    collection_name: str
    description: Optional[str] = None
    embedding_model: Optional[str] = "sentence-transformers/all-MiniLM-L6-v2"

class VectorCollectionResponse(BaseModel):
    id: str
    collection_name: str
    description: Optional[str]
    embedding_model: str
    created_at: datetime
    is_active: bool 