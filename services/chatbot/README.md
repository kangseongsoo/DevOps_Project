# Redis 기반 ChatBot API

Redis를 사용해서 대화 내용을 저장하고 세션 ID로 대화를 구분하는 GPT 챗봇 API입니다.

## 프로젝트 구조

```
app/
├── __init__.py          # 패키지 초기화
├── main.py             # FastAPI 엔드포인트
├── config.py           # 환경 변수 및 설정
├── models.py           # Pydantic 모델 정의
├── database.py         # Redis 연결 및 데이터 관리
└── services.py         # 비즈니스 로직 (ChatGPT 서비스)
```

## 기능

- 세션 ID 기반 대화 관리
- Redis를 통한 대화 내용 저장 (24시간 TTL)
- 대화 기록 조회 및 삭제
- OpenAI GPT-3.5-turbo 모델 사용
- 모듈화된 코드 구조

## 설치 및 실행

### 1. Redis 실행 (Docker)

```bash
# Redis Docker 컨테이너 실행
docker-compose up -d redis

# Redis 상태 확인
docker ps
```

### 2. 환경 변수 설정

```bash
# env.example을 .env로 복사
cp env.example .env

# .env 파일을 편집하여 OpenAI API 키 설정
```

### 3. 의존성 설치 및 API 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# API 실행
python -m app.main
# 또는
python app/main.py
```

## 모듈 설명

### `config.py`
- 환경 변수 관리
- 설정값 검증
- OpenAI, Redis, API 설정

### `models.py`
- Pydantic 모델 정의
- 요청/응답 스키마
- 타입 안전성 보장

### `database.py`
- Redis 연결 관리
- 대화 데이터 CRUD 작업
- 연결 상태 모니터링

### `services.py`
- ChatGPT 서비스 로직
- 대화 기록 처리
- 메시지 변환 로직

### `main.py`
- FastAPI 엔드포인트 정의
- HTTP 요청/응답 처리
- 에러 핸들링

## API 엔드포인트

### 1. 채팅 API (`POST /chat`)

세션 ID를 사용해서 대화를 관리합니다.

```json
// 요청
{
    "message": "안녕하세요!",
    "session_id": "optional-session-id"  // 없으면 자동 생성
}

// 응답
{
    "response": "안녕하세요! 무엇을 도와드릴까요?",
    "session_id": "generated-uuid",
    "status": "success"
}
```

### 2. 간단한 채팅 API (`POST /simple-chat`)

대화 기록 없이 단순 응답만 제공합니다.

```json
// 요청
{
    "message": "안녕하세요!"
}

// 응답
{
    "response": "안녕하세요! 무엇을 도와드릴까요?",
    "status": "success"
}
```

### 3. 대화 기록 조회 (`GET /conversation/{session_id}`)

특정 세션의 대화 내용을 조회합니다.

```json
// 응답
{
    "session_id": "your-session-id",
    "conversation": [
        {
            "role": "user",
            "content": "안녕하세요!"
        },
        {
            "role": "assistant",
            "content": "안녕하세요! 무엇을 도와드릴까요?"
        }
    ],
    "status": "success"
}
```

### 4. 대화 기록 삭제 (`DELETE /conversation/{session_id}`)

특정 세션의 대화 내용을 삭제합니다.

### 5. 상태 확인 (`GET /health`)

API와 Redis 연결 상태를 확인합니다.

## 사용 예시

### curl 예시

```bash
# 새로운 대화 시작
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "안녕하세요!"}'

# 기존 세션으로 대화 계속
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "오늘 날씨는 어때요?", "session_id": "your-session-id"}'

# 대화 기록 조회
curl -X GET "http://localhost:8000/conversation/your-session-id"

# 대화 기록 삭제
curl -X DELETE "http://localhost:8000/conversation/your-session-id"
```

### Python 예시

```python
import requests

# 새로운 대화 시작
response = requests.post("http://localhost:8000/chat", 
    json={"message": "안녕하세요!"})
data = response.json()
session_id = data["session_id"]

# 기존 세션으로 대화 계속
response = requests.post("http://localhost:8000/chat", 
    json={
        "message": "오늘 날씨는 어때요?",
        "session_id": session_id
    })
```

## 설정

### 환경 변수

- `OPENAI_API_KEY`: OpenAI API 키 (필수)
- `OPENAI_MODEL`: 사용할 모델 (기본값: gpt-3.5-turbo)
- `OPENAI_TEMPERATURE`: 모델 온도 (기본값: 0.7)
- `REDIS_HOST`: Redis 호스트 (기본값: localhost)
- `REDIS_PORT`: Redis 포트 (기본값: 6379)
- `REDIS_PASSWORD`: Redis 비밀번호 (선택사항)
- `REDIS_TTL`: 대화 데이터 TTL 초 (기본값: 86400 = 24시간)
- `API_HOST`: API 호스트 (기본값: 0.0.0.0)
- `API_PORT`: API 포트 (기본값: 8000)

### Redis 설정

- 대화 데이터는 설정된 TTL 후 자동 삭제됩니다
- Redis 키 형식: `conversation:{session_id}`

## 개발

### 코드 구조의 장점

1. **관심사 분리**: 각 모듈이 명확한 책임을 가짐
2. **테스트 용이성**: 각 모듈을 독립적으로 테스트 가능
3. **유지보수성**: 기능별로 코드가 분리되어 수정이 용이
4. **확장성**: 새로운 기능 추가 시 해당 모듈만 수정
5. **재사용성**: 다른 프로젝트에서 모듈 재사용 가능 