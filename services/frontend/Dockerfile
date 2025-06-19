FROM node:18-alpine

WORKDIR /app

# 패키지 파일 복사
COPY package*.json ./

# 의존성 설치
RUN npm install

# 앱 소스 복사
COPY . .

# 포트 노출
EXPOSE 3000

# 앱 실행
CMD ["npm", "start"] 