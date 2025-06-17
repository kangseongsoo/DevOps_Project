#!/usr/bin/env python3
import requests
import json
import sys

def test_chatbot():
    base_url = "http://localhost:8000"
    
    print("🤖 ChatBot API 테스트 도구")
    print("=" * 40)
    
    # 서버 상태 확인
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ 서버가 정상적으로 실행 중입니다.")
        else:
            print("❌ 서버 상태 확인 실패")
            return
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        return
    
    print("\n명령어:")
    print("- 메시지 입력: 일반 텍스트")
    print("- 종료: 'quit' 또는 'exit'")
    print("- 도움말: 'help'")
    print("-" * 40)
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료']:
                print("👋 채팅을 종료합니다.")
                break
            
            if user_input.lower() == 'help':
                print("\n📋 사용 가능한 명령어:")
                print("- quit/exit: 프로그램 종료")
                print("- clear: 대화 기록 초기화")
                print("- history: 대화 기록 보기")
                continue
            
            if user_input.lower() == 'clear':
                conversation_history = []
                print("🗑️ 대화 기록이 초기화되었습니다.")
                continue
            
            if user_input.lower() == 'history':
                print("\n📜 대화 기록:")
                for i, msg in enumerate(conversation_history, 1):
                    role = "👤" if msg["role"] == "user" else "🤖"
                    print(f"{i}. {role} {msg['content'][:50]}...")
                continue
            
            if not user_input:
                print("⚠️ 메시지를 입력해주세요.")
                continue
            
            # API 호출
            payload = {
                "message": user_input,
                "conversation_history": conversation_history
            }
            
            print("🤖 Bot: 생각 중...", end="", flush=True)
            
            response = requests.post(
                f"{base_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print("\r", end="")  # 로딩 메시지 지우기
            
            if response.status_code == 200:
                result = response.json()
                bot_response = result["response"]
                print(f"🤖 Bot: {bot_response}")
                
                # 대화 기록 업데이트
                conversation_history.append({"role": "user", "content": user_input})
                conversation_history.append({"role": "assistant", "content": bot_response})
                
            else:
                print(f"❌ 오류 발생: {response.status_code}")
                print(f"상세: {response.text}")
                
        except KeyboardInterrupt:
            print("\n\n👋 Ctrl+C로 종료되었습니다.")
            break
        except Exception as e:
            print(f"\n❌ 예상치 못한 오류: {e}")

def test_endpoints():
    """모든 엔드포인트 테스트"""
    base_url = "http://localhost:8000"
    
    print("🧪 API 엔드포인트 테스트")
    print("=" * 40)
    
    tests = [
        ("GET", "/", "기본 엔드포인트"),
        ("GET", "/health", "헬스체크"),
        ("POST", "/simple-chat", "간단한 채팅", {"message": "테스트 메시지"}),
        ("POST", "/chat", "대화 채팅", {
            "message": "안녕하세요!",
            "conversation_history": []
        })
    ]
    
    for method, endpoint, description, data in tests:
        try:
            print(f"\n📡 {description} 테스트...")
            
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}")
            else:
                response = requests.post(
                    f"{base_url}{endpoint}",
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
            
            if response.status_code == 200:
                print(f"✅ 성공 ({response.status_code})")
                result = response.json()
                if isinstance(result, dict) and len(str(result)) < 200:
                    print(f"   응답: {result}")
                else:
                    print(f"   응답 길이: {len(str(result))} 문자")
            else:
                print(f"❌ 실패 ({response.status_code})")
                print(f"   오류: {response.text}")
                
        except Exception as e:
            print(f"❌ 연결 오류: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_endpoints()
    else:
        test_chatbot() 