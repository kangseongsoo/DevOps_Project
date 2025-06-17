import uuid
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from config import settings
from database import redis_manager
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def _convert_to_langchain_messages(self, conversation_history: List[Dict[str, Any]]) -> List:
        """대화 기록을 Langchain 메시지 형식으로 변환"""
        messages = []
        
        for msg in conversation_history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg.get("content", "")))
        
        return messages
    
    def chat_with_history(self, message: str, session_id: str = None) -> tuple[str, str]:
        """대화 기록을 포함한 채팅"""
        logger.info(f"chat_with_history 호출: message={message}, session_id={session_id}")
        # 세션 ID가 없으면 새로 생성
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"새로운 session_id 생성: {session_id}")
        # Redis에서 기존 대화 내용 불러오기
        conversation_history = redis_manager.get_conversation(session_id)
        logger.info(f"기존 대화 기록 불러옴: {len(conversation_history)}개 메시지")
        # 대화 기록을 Langchain 메시지 형식으로 변환
        messages = self._convert_to_langchain_messages(conversation_history)
        # 현재 사용자 메시지 추가
        messages.append(HumanMessage(content=message))
        try:
            # GPT 모델을 통해 응답 생성
            response = self.llm.invoke(messages)
            # 사용자 메시지를 대화 기록에 추가
            redis_manager.add_message_to_conversation(session_id, "user", message)
            # AI 응답을 대화 기록에 추가
            redis_manager.add_message_to_conversation(session_id, "assistant", response.content)
            logger.info(f"응답 생성 및 저장 완료: session_id={session_id}")
            return response.content, session_id
        except Exception as e:
            logger.error(f"chat_with_history 오류: {str(e)}")
            raise
    
    def simple_chat(self, message: str) -> str:
        """단순 채팅 (대화 기록 없음)"""
        logger.info(f"simple_chat 호출: message={message}")
        human_message = HumanMessage(content=message)
        try:
            response = self.llm.invoke([human_message])
            logger.info("simple_chat 응답 생성 완료")
            return response.content
        except Exception as e:
            logger.error(f"simple_chat 오류: {str(e)}")
            raise

# 채팅 서비스 인스턴스
chat_service = ChatService() 