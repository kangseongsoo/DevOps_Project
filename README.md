# DevOps 프로젝트

마이크로서비스 아키텍처 기반의 확장 가능한 DevOps 프로젝트입니다.

## 🏗️ 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   Chatbot API   │    │     Redis       │
│  (Reverse Proxy)│────│   (FastAPI)     │────│   (Memory DB)   │
│     :80         │    │     :7000       │    │     :6379       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 프로젝트 구조

```
DevOps_Project/
├── docker-compose.yml          # 전체 서비스 오케스트레이션
├── env.example                # 환경변수 예시
├── README.md                  # 프로젝트 문서
├── services/                  # 각 서비스별 디렉토리
│   ├── redis/                 # Redis 설정
│   │   └── redis.conf
│   ├── chatbot/              # 챗봇 서비스
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   └── main.py
│   │   └── tests/
│   └── [향후 추가 서비스들]
├── shared/                   # 공통 설정
│   └── nginx/               # 리버스 프록시
│       ├── nginx.conf
│       └── conf.d/
└── scripts/                 # 유틸리티 스크립트
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 환경변수 파일 생성
cp env.example .env

# OpenAI API 키 설정
echo "OPENAI_API_KEY=your_api_key_here" >> .env
```

### 2. 서비스 실행

```bash
# 모든 서비스 실행
docker compose up --build

# 백그라운드 실행
docker compose up -d --build
```

### 3. 서비스 확인

```bash
# 서비스 상태 확인
docker compose ps

# 로그 확인
docker compose logs -f chatbot
```

## 🔗 API 엔드포인트

### 직접 접근 (개발용)
- **챗봇 API**: http://localhost:7000
- **API 문서**: http://localhost:7000/docs
- **헬스체크**: http://localhost:7000/health

### Nginx를 통한 접근 (운영용)
- **API**: http://localhost/api/
- **헬스체크**: http://localhost/health

## 📊 주요 기능

### 현재 구현된 기능
- ✅ **챗봇 API**: OpenAI GPT 기반 대화형 AI
- ✅ **Redis 메모리**: 세션별 대화 히스토리 저장
- ✅ **리버스 프록시**: Nginx를 통한 로드밸런싱
- ✅ **헬스체크**: 서비스 상태 모니터링
- ✅ **Docker 컨테이너화**: 마이크로서비스 아키텍처

### 향후 확장 계획
- 🔄 **웹 UI**: React/Vue.js 기반 프론트엔드
- 🔄 **모니터링**: Prometheus + Grafana
- 🔄 **로그 수집**: ELK Stack
- 🔄 **CI/CD**: GitHub Actions
- 🔄 **데이터베이스**: PostgreSQL
- 🔄 **인증/인가**: JWT 기반 보안

## 🛠️ 개발 가이드

### 새로운 서비스 추가

1. `services/` 디렉토리에 새 서비스 폴더 생성
2. `Dockerfile` 및 필요한 설정 파일 작성
3. `docker-compose.yml`에 서비스 정의 추가
4. Nginx 설정에 라우팅 규칙 추가

### 환경별 설정

- **개발환경**: `docker compose up`
- **운영환경**: `docker compose -f docker-compose.prod.yml up`

## 🔧 유용한 명령어

```bash
# 특정 서비스만 재시작
docker compose restart chatbot

# 로그 실시간 확인
docker compose logs -f

# 컨테이너 내부 접근
docker compose exec chatbot bash

# 서비스 스케일링
docker compose up --scale chatbot=3

# 정리
docker compose down -v
```

## 📝 라이센스

MIT License

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request 