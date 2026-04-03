# 02. 배포 및 보안 가이드 (Deployment & Security)

이 문서는 ClosingSHIN 프로젝트를 Synology DS218+ NAS에 Docker로 배포하는 방법과 시스템의 안정성을 유지하기 위한 주요 보안 로직을 설명합니다.

---

## 1. Synology DS218+ Docker 배포 가이드 (GUI 기반)

프로젝트를 NAS에 24시간 안정적으로 가동하기 위한 배포 프로세스입니다.

### 전제 조건
- Windows PC에 Docker Desktop 설치
- DS218+ DSM 7.x 및 Container Manager 패키지 설치
- DDNS (예: `drspike.synology.me`), 포트포워딩 설정 완료

### 단계별 배포 과정 요약

**Phase 1: PC에서 이미지 빌드 및 전송**
1. PC 터미널에서 이미지 빌드: `docker build -t closingshin:latest .`
2. 이미지 내보내기: `docker save closingshin:latest -o closingshin.tar` (또는 Docker GUI 사용)
3. NAS의 `docker/closingshin/` 폴더로 `.tar` 파일과 `docker-compose.yml`, `.env` 파일 복사

**Phase 2: 과거 데이터 동기화**
- PC의 `Scripts/data/` 및 `Scripts/results/` 폴더를 NAS의 동일 경로로 복사하여 기존 데이터와 분석 결과를 유지합니다.

**Phase 3: Container Manager로 실행**
1. **이미지 탭:** `.tar` 파일을 선택하여 이미지를 '가져오기' 합니다.
2. **프로젝트 탭:** '생성'을 클릭하고, 경로를 `docker/closingshin`으로 지정합니다.
3. `docker-compose.yml`이 자동 인식되면 구성 확인 후 컨테이너를 실행합니다.

**Phase 4: 역방향 프록시 (HTTPS 설정)**
1. **DSM 제어판 > 보안 > 인증서:** Let's Encrypt를 통해 서비스 도메인 인증서를 발급받습니다.
2. **역방향 프록시:** HTTPS(443) 요청을 localhost의 HTTP(3000)으로 포워딩하는 규칙을 추가합니다.
3. 공유기 설정에서 443과 80 포트를 NAS IP로 포워딩합니다.

> **Troubleshooting:** 외부 망(LTE/5G)에서 접속 시 공유기 설정 페이지로 연결될 경우, 공유기의 '원격 관리 포트(Remote Management)'와 충돌 우려가 있으니 공유기 설정을 점검해야 합니다.

---

## 2. 시스템 보안 및 안정성 (System Security & Stability)

데이터 파이프라인의 백그라운드 스크립트 실행이 꼬이거나 시스템 리소스를 고갈시키지 않도록 설계된 보안 로직들입니다.

### 2-1. 프로세스 격리 및 중복 실행 방지 (Process Isolation)
사용자가 대시보드에서 스크립트 실행 버튼을 여러 번 누르더라도 프로세스가 중복으로 띄워지는 것을 막습니다.
- **API 레이어:** Next.js 라우트 레벨에서 `debounce` 및 플래그 제어를 통해 동일한 스크립트가 이미 실행 중이면 재요청을 즉각 거부합니다. 
- 이로 인해 데이터 파일(JSON/CSV) 입출력 충돌(Race Condition)을 원천 차단합니다.

### 2-2. 환경 격리 (Environment Security)
Python 스크립트는 전역 환경이 아닌 격리된 가상 환경(`venv`) 내에서만 제한적으로 실행됩니다.
- 외부 API 토큰, Gemini 설정 등 민감한 환경 변수는 소스코드에 포함되지 않으며 외부 `.env` 파일로 완전히 격리합니다. 서버(.env 볼륨 마운트)와 보안 철칙에 따라 관리됩니다.

### 2-3. 입력 검증 (Input Validation)
- API (예: `/api/run-scan`)로 전달되는 파라미터(`date` 등)는 정해진 규격(`YYYY-MM-DD`)인지 라우트 내부에서 철저하게 먼저 검증합니다.
- 잘못된 데이터 주입을 허용하지 않아 파이썬 스크립트 파싱 오류와 스크립트 크래시를 방지합니다.

### 2-4. 분산 프로세스 통합 관리
- 컨테이너 시작 시 실행되는 `start.sh`를 통해 Next.js 웹 서버(`port 3000`)와 스케줄러 상태 API 서버(`port 3001`)가 병렬 실행됩니다.
- 둘 중 하나라도 예기치 않게 종료될 경우 시스템 일관성을 위해 컨테이너 전체를 재시작 하도록(`wait -n`) 이중 잠금장치가 마련되어 있습니다.
