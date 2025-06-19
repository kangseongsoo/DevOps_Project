from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings
from database import mariadb_manager

# 비밀번호 암호화 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 토큰 보안 설정
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """JWT 토큰 검증"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 유효하지 않습니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """현재 사용자 정보 가져오기"""
    token = credentials.credentials
    username = verify_token(token)
    
    # 데이터베이스에서 사용자 정보 조회
    query = "SELECT id, username, email, created_at, is_active FROM users WHERE username = %s AND is_active = 1"
    result = await mariadb_manager.execute_query(query, (username,))
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다",
        )
    
    user_data = result[0]
    return {
        "id": user_data[0],
        "username": user_data[1],
        "email": user_data[2],
        "created_at": user_data[3],
        "is_active": user_data[4]
    }

async def authenticate_user(username: str, password: str):
    """사용자 인증"""
    query = "SELECT id, username, email, password_hash, created_at, is_active FROM users WHERE username = %s AND is_active = 1"
    result = await mariadb_manager.execute_query(query, (username,))
    
    if not result:
        return False
    
    user_data = result[0]
    if not verify_password(password, user_data[3]):
        return False
    
    return {
        "id": user_data[0],
        "username": user_data[1],
        "email": user_data[2],
        "created_at": user_data[4],
        "is_active": user_data[5]
    } 