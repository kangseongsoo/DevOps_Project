from fastapi import FastAPI, HTTPException
from config import settings
from models import (
    ChatRequest, SimpleChatRequest, ChatResponse, 
    ConversationResponse, DeleteResponse, HealthResponse
)
from services import chat_service
from database import redis_manager

app = FastAPI(title="ChatBot API", description="GPT를 사용한 챗봇 서비스")

@app.get("/")
async def root():
    return {"message": "ChatBot API가 실행 중입니다!"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    redis_status = "connected" if redis_manager.is_connected() else "disconnected"
    return HealthResponse(
        status="healthy",
        redis=redis_status
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response_content, session_id = chat_service.chat_with_history(
            message=request.message,
            session_id=request.session_id
        )
        
        return ChatResponse(
            response=response_content,
            session_id=session_id,
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"챗봇 응답 생성 중 오류가 발생했습니다: {str(e)}"
        )

@app.post("/simple-chat")
async def simple_chat(request: SimpleChatRequest):
    """간단한 챗봇 엔드포인트 (이전 대화 기록 없이)"""
    try:
        response_content = chat_service.simple_chat(request.message)
        
        return {
            "response": response_content,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"챗봇 응답 생성 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/conversation/{session_id}", response_model=ConversationResponse)
async def get_conversation(session_id: str):
    """특정 세션의 대화 내용 조회"""
    try:
        conversation = redis_manager.get_conversation(session_id)
        return ConversationResponse(
            session_id=session_id,
            conversation=conversation,
            status="success"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"대화 내용 조회 중 오류가 발생했습니다: {str(e)}"
        )

@app.delete("/conversation/{session_id}", response_model=DeleteResponse)
async def delete_conversation(session_id: str):
    """특정 세션의 대화 내용 삭제"""
    try:
        success = redis_manager.delete_conversation(session_id)
        
        if success:
            return DeleteResponse(
                session_id=session_id,
                message="대화 내용이 삭제되었습니다.",
                status="success"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="대화 내용 삭제에 실패했습니다."
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"대화 내용 삭제 중 오류가 발생했습니다: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
