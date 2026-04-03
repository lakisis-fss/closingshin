#!/bin/bash
# ClosingSHIN - Container Startup Script
# Next.js (port 3000) + Scheduler (port 3001) 동시 실행

echo "=== ClosingSHIN Starting ==="
echo "Time: $(date)"

# 1. Next.js 프로덕션 서버 시작 (백그라운드)
echo "[Start] Next.js production server on port 3000..."
cd /app/frontend
npm run start &
NEXTJS_PID=$!

# 2. Node.js Scheduler 시작 (백그라운드)
echo "[Start] Scheduler on port 3001..."
cd /app/frontend
tsx backend/scheduler.ts &
SCHEDULER_PID=$!

echo "[Start] All services running."
echo "  - Next.js PID: $NEXTJS_PID"
echo "  - Scheduler PID: $SCHEDULER_PID"

# 두 프로세스 중 하나라도 죽으면 컨테이너 종료 (docker restart policy가 재시작)
wait -n $NEXTJS_PID $SCHEDULER_PID
EXIT_CODE=$?

echo "[Error] A process exited with code $EXIT_CODE. Shutting down..."
kill $NEXTJS_PID $SCHEDULER_PID 2>/dev/null
exit $EXIT_CODE
