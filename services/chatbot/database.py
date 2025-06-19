import json
import aiomysql
from typing import List, Dict, Any, Optional
import redis
from config import settings

class MariaDBManager:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """MariaDB 연결 풀 생성"""
        try:
            self.pool = await aiomysql.create_pool(
                host=settings.MARIADB_HOST,
                port=settings.MARIADB_PORT,
                user=settings.MARIADB_USER,
                password=settings.MARIADB_PASSWORD,
                db=settings.MARIADB_DATABASE,
                charset='utf8mb4',
                autocommit=True,
                minsize=1,
                maxsize=10
            )
            print("MariaDB 연결 성공!")
        except Exception as e:
            print(f"MariaDB 연결 실패: {e}")
            self.pool = None
    
    async def close(self):
        """연결 풀 종료"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
    
    def is_connected(self) -> bool:
        """MariaDB 연결 상태 확인"""
        return self.pool is not None
    
    async def execute_query(self, query: str, params: tuple = None):
        """쿼리 실행"""
        if not self.pool:
            return None
        
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchall()
    
    async def execute_insert(self, query: str, params: tuple = None):
        """INSERT 쿼리 실행 후 ID 반환"""
        if not self.pool:
            return None
        
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return cursor.lastrowid

class RedisManager:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self._connect()
    
    def _connect(self):
        """Redis 연결"""
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Redis 연결 테스트
            self.client.ping()
            print("Redis 연결 성공!")
        except Exception as e:
            print(f"Redis 연결 실패: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Redis 연결 상태 확인"""
        return self.client is not None
    
    def get_conversation_key(self, session_id: str) -> str:
        """세션 ID로 Redis 키 생성"""
        return f"conversation:{session_id}"
    
    def save_conversation(self, session_id: str, conversation: List[Dict[str, Any]]) -> bool:
        """대화 내용을 Redis에 저장"""
        if not self.client:
            return False
        
        try:
            key = self.get_conversation_key(session_id)
            self.client.set(key, json.dumps(conversation), ex=settings.REDIS_TTL)
            return True
        except Exception as e:
            print(f"Redis 저장 오류: {e}")
            return False
    
    def get_conversation(self, session_id: str) -> List[Dict[str, Any]]:
        """Redis에서 대화 내용 불러오기"""
        if not self.client:
            return []
        
        try:
            key = self.get_conversation_key(session_id)
            conversation_data = self.client.get(key)
            if conversation_data:
                return json.loads(conversation_data)
            return []
        except Exception as e:
            print(f"Redis 조회 오류: {e}")
            return []
    
    def add_message_to_conversation(self, session_id: str, role: str, content: str):
        """대화에 새 메시지 추가"""
        conversation = self.get_conversation(session_id)
        conversation.append({
            "role": role,
            "content": content
        })
        self.save_conversation(session_id, conversation)
    
    def delete_conversation(self, session_id: str) -> bool:
        """특정 세션의 대화 내용 삭제"""
        if not self.client:
            return False
        
        try:
            key = self.get_conversation_key(session_id)
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Redis 삭제 오류: {e}")
            return False

# 데이터베이스 매니저 인스턴스
redis_manager = RedisManager()
mariadb_manager = MariaDBManager() 