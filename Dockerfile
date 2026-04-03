# ============================================
# ClosingSHIN - Docker Image
# Node.js 20 + Python 3.11 Multi-Runtime
# Target: Synology DS218+ (x86_64)
# ============================================

# --- Stage 1: Build ---
FROM node:20-slim AS builder

# Python 3 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv python3-dev \
    build-essential tzdata && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python 의존성 설치 (캐시 활용을 위해 먼저)
COPY requirements.txt ./
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Node.js 의존성 설치
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN cd frontend && npm ci --ignore-scripts

# 소스 코드 복사
COPY frontend/ ./frontend/
COPY Scripts/ ./Scripts/
COPY .env ./

# Next.js 프로덕션 빌드
RUN cd frontend && npm run build

# --- Stage 2: Production ---
FROM node:20-slim

# Python 3 런타임만 설치 (dev 도구 제외)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 python3-venv tzdata fonts-nanum && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 빌드된 결과물 복사
COPY --from=builder /app/venv /app/venv
COPY --from=builder /app/frontend /app/frontend
COPY --from=builder /app/Scripts /app/Scripts
COPY --from=builder /app/.env /app/.env

# tsx 글로벌 설치 (스케줄러용)
RUN npm install -g tsx

# 시작 스크립트 복사
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Python path 설정
ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONIOENCODING=utf-8
ENV NODE_ENV=production

# Next.js 포트
EXPOSE 3000
# Scheduler 상태 API 포트
EXPOSE 3001

CMD ["/app/start.sh"]
