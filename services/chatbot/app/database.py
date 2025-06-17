import json
from typing import List, Dict, Any, Optional
import redis
from config import settings

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

# Redis 매니저 인스턴스
redis_manager = RedisManager() 