#!/bin/bash

# DevOps 프로젝트 초기 설정 스크립트

set -e

echo "🚀 DevOps 프로젝트 초기 설정을 시작합니다..."

# 환경변수 파일 생성
if [ ! -f .env ]; then
    echo "📝 환경변수 파일을 생성합니다..."
    cp env.example .env
    echo "✅ .env 파일이 생성되었습니다. OpenAI API 키를 설정해주세요."
else
    echo "⚠️ .env 파일이 이미 존재합니다."
fi

# Docker 및 Docker Compose 설치 확인
echo "🔍 Docker 설치 상태를 확인합니다..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다. Docker를 먼저 설치해주세요."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose가 설치되지 않았습니다. Docker Compose를 먼저 설치해주세요."
    exit 1
fi

echo "✅ Docker 환경이 준비되었습니다."

# 필요한 디렉토리 권한 설정
echo "🔧 디렉토리 권한을 설정합니다..."
chmod +x scripts/*.sh
mkdir -p logs
chmod 755 logs

# Docker 이미지 빌드
echo "🏗️ Docker 이미지를 빌드합니다..."
docker compose build

echo "🎉 초기 설정이 완료되었습니다!"
echo ""
echo "다음 단계:"
echo "1. .env 파일에서 OPENAI_API_KEY를 설정하세요"
echo "2. 'docker compose up' 명령으로 서비스를 시작하세요"
echo "3. http://localhost:8000/docs 에서 API 문서를 확인하세요" 