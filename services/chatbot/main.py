import logging
import uuid
from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from models import (
    ChatRequest, SimpleChatRequest, ChatResponse, 
    ConversationResponse, DeleteResponse, HealthResponse,
    UserCreate, UserLogin, UserResponse, Token,
    ChatSessionCreate, ChatSessionResponse
)
from services import chat_service
from database import redis_manager, mariadb_manager
from auth import (
    get_password_hash, authenticate_user, create_access_token, 
    get_current_user, get_password_hash
)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="ChatBot API", description="GPT를 사용한 챗봇 서비스")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 실제 도메인으로 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 MariaDB 연결"""
    await mariadb_manager.connect()

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 MariaDB 연결 종료"""
    await mariadb_manager.close()

@app.get("/")
async def root():
    logger.info("루트 엔드포인트 호출됨")
    return {"message": "ChatBot API가 실행 중입니다!"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    redis_status = "connected" if redis_manager.is_connected() else "disconnected"
    mariadb_status = "connected" if mariadb_manager.is_connected() else "disconnected"
    logger.info(f"/health 체크: redis={redis_status}, mariadb={mariadb_status}")
    return HealthResponse(
        status="healthy",
        redis=redis_status,
        mariadb=mariadb_status
    )

# 사용자 인증 엔드포인트
@app.post("/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """회원가입"""
    try:
        logger.info(f"회원가입 요청: username={user.username}, email={user.email}")
        
        # 중복 확인
        check_query = "SELECT id FROM users WHERE username = %s OR email = %s"
        existing_user = await mariadb_manager.execute_query(check_query, (user.username, user.email))
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="이미 존재하는 사용자명 또는 이메일입니다"
            )
        
        # 비밀번호 해싱
        hashed_password = get_password_hash(user.password)
        
        # 사용자 생성
        insert_query = """
            INSERT INTO users (username, email, password_hash) 
            VALUES (%s, %s, %s)
        """
        user_id = await mariadb_manager.execute_insert(
            insert_query, 
            (user.username, user.email, hashed_password)
        )
        
        # 생성된 사용자 정보 반환
        user_query = "SELECT id, username, email, created_at, is_active FROM users WHERE id = %s"
        user_data = await mariadb_manager.execute_query(user_query, (user_id,))
        
        logger.info(f"회원가입 성공: user_id={user_id}")
        return UserResponse(
            id=user_data[0][0],
            username=user_data[0][1],
            email=user_data[0][2],
            created_at=user_data[0][3],
            is_active=user_data[0][4]
        )
        
    except Exception as e:
        logger.error(f"회원가입 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"회원가입 중 오류가 발생했습니다: {str(e)}"
        )

@app.post("/auth/login", response_model=Token)
async def login_user(user: UserLogin):
    """로그인"""
    try:
        logger.info(f"로그인 요청: username={user.username}")
        
        # 사용자 인증
        authenticated_user = await authenticate_user(user.username, user.password)
        if not authenticated_user:
            raise HTTPException(
                status_code=401,
                detail="잘못된 사용자명 또는 비밀번호입니다"
            )
        
        # 토큰 생성
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": authenticated_user["username"]}, 
            expires_delta=access_token_expires
        )
        
        logger.info(f"로그인 성공: username={user.username}")
        return Token(access_token=access_token, token_type="bearer")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그인 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"로그인 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """현재 사용자 정보 조회"""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        created_at=current_user["created_at"],
        is_active=current_user["is_active"]
    )

# 채팅 세션 관리
@app.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session: ChatSessionCreate,
    current_user: dict = Depends(get_current_user)
):
    """새로운 채팅 세션 생성"""
    try:
        session_id = str(uuid.uuid4())
        
        insert_query = """
            INSERT INTO chat_sessions (id, user_id, title) 
            VALUES (%s, %s, %s)
        """
        await mariadb_manager.execute_insert(
            insert_query, 
            (session_id, current_user["id"], session.title)
        )
        
        # 생성된 세션 정보 반환
        session_query = """
            SELECT id, title, created_at, updated_at, is_active 
            FROM chat_sessions WHERE id = %s
        """
        session_data = await mariadb_manager.execute_query(session_query, (session_id,))
        
        return ChatSessionResponse(
            id=session_data[0][0],
            title=session_data[0][1],
            created_at=session_data[0][2],
            updated_at=session_data[0][3],
            is_active=session_data[0][4]
        )
        
    except Exception as e:
        logger.error(f"세션 생성 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"세션 생성 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/sessions")
async def get_user_sessions(current_user: dict = Depends(get_current_user)):
    """사용자의 채팅 세션 목록 조회"""
    try:
        query = """
            SELECT id, title, created_at, updated_at, is_active 
            FROM chat_sessions 
            WHERE user_id = %s AND is_active = 1
            ORDER BY updated_at DESC
        """
        sessions = await mariadb_manager.execute_query(query, (current_user["id"],))
        
        return [
            ChatSessionResponse(
                id=session[0],
                title=session[1],
                created_at=session[2],
                updated_at=session[3],
                is_active=session[4]
            )
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"세션 목록 조회 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"세션 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )

# 챗봇 엔드포인트 (인증 필요)
@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        logger.info(f"/chat 요청: message={request.message}, session_id={request.session_id}, user_id={current_user['id']}")
        
        # 세션 검증 (세션이 현재 사용자의 것인지 확인)
        if request.session_id:
            session_query = "SELECT user_id FROM chat_sessions WHERE id = %s AND is_active = 1"
            session_result = await mariadb_manager.execute_query(session_query, (request.session_id,))
            
            if not session_result or session_result[0][0] != current_user["id"]:
                raise HTTPException(
                    status_code=403,
                    detail="해당 세션에 접근할 권한이 없습니다"
                )
        
        response_content, session_id = chat_service.chat_with_history(
            message=request.message,
            session_id=request.session_id
        )
        
        # 채팅 히스토리를 데이터베이스에 저장
        if session_id:
            # 사용자 메시지 저장
            await mariadb_manager.execute_insert(
                "INSERT INTO chat_history (session_id, user_id, role, content) VALUES (%s, %s, %s, %s)",
                (session_id, current_user["id"], "user", request.message)
            )
            
            # 봇 응답 저장
            await mariadb_manager.execute_insert(
                "INSERT INTO chat_history (session_id, user_id, role, content) VALUES (%s, %s, %s, %s)",
                (session_id, current_user["id"], "assistant", response_content)
            )
        
        logger.info(f"/chat 응답: session_id={session_id}")
        return ChatResponse(
            response=response_content,
            session_id=session_id,
            status="success"
        )
    except Exception as e:
        logger.error(f"/chat 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"챗봇 응답 생성 중 오류가 발생했습니다: {str(e)}"
        )

@app.post("/simple-chat")
async def simple_chat(request: SimpleChatRequest):
    """간단한 챗봇 엔드포인트 (이전 대화 기록 없이, 인증 불필요)"""
    try:
        logger.info(f"/simple-chat 요청: message={request.message}")
        response_content = chat_service.simple_chat(request.message)
        logger.info("/simple-chat 응답 완료")
        return {
            "response": response_content,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"/simple-chat 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"챗봇 응답 생성 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/conversation/{session_id}", response_model=ConversationResponse)
async def get_conversation(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """특정 세션의 대화 내용 조회"""
    try:
        # 세션 권한 확인
        session_query = "SELECT user_id FROM chat_sessions WHERE id = %s AND is_active = 1"
        session_result = await mariadb_manager.execute_query(session_query, (session_id,))
        
        if not session_result or session_result[0][0] != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="해당 세션에 접근할 권한이 없습니다"
            )
        
        logger.info(f"/conversation/{session_id} 조회 요청")
        conversation = redis_manager.get_conversation(session_id)
        logger.info(f"/conversation/{session_id} 조회 성공")
        return ConversationResponse(
            session_id=session_id,
            conversation=conversation,
            status="success"
        )
    except Exception as e:
        logger.error(f"/conversation/{session_id} 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"대화 내용 조회 중 오류가 발생했습니다: {str(e)}"
        )

@app.delete("/conversation/{session_id}", response_model=DeleteResponse)
async def delete_conversation(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """특정 세션의 대화 내용 삭제"""
    try:
        # 세션 권한 확인
        session_query = "SELECT user_id FROM chat_sessions WHERE id = %s AND is_active = 1"
        session_result = await mariadb_manager.execute_query(session_query, (session_id,))
        
        if not session_result or session_result[0][0] != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="해당 세션에 접근할 권한이 없습니다"
            )
        
        logger.info(f"/conversation/{session_id} 삭제 요청")
        
        # Redis에서 대화 내용 삭제
        redis_success = redis_manager.delete_conversation(session_id)
        
        # 데이터베이스에서 세션 비활성화
        await mariadb_manager.execute_query(
            "UPDATE chat_sessions SET is_active = 0 WHERE id = %s",
            (session_id,)
        )
        
        if redis_success:
            logger.info(f"/conversation/{session_id} 삭제 성공")
            return DeleteResponse(
                session_id=session_id,
                message="대화 내용이 삭제되었습니다.",
                status="success"
            )
        else:
            logger.error(f"/conversation/{session_id} 삭제 실패")
            raise HTTPException(
                status_code=500,
                detail="대화 내용 삭제에 실패했습니다."
            )
    except Exception as e:
        logger.error(f"/conversation/{session_id} 삭제 중 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"대화 내용 삭제 중 오류가 발생했습니다: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
