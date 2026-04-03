# PocketBase 마이그레이션 완료 보고서

본 문서는 로컬 파일 시스템 기반의 데이터 관리 체계에서 PocketBase 데이터베이스 환경으로의 마이그레이션 수행 결과를 정리합니다.

## 마이그레이션 대상 및 결과

| 대상 항목 | 기존 방식 | 변경된 방식 (PocketBase) | 상태 |
| :--- | :--- | :--- | :--- |
| **포트폴리오 상태** | `portfolio_status.json` | `settings` 컬렉션 (key: portfolio_status) | ✅ 완료 |
| **스캔 진행률** | `scan_progress.json` | `settings` 컬렉션 (key: scan_progress) | ✅ 완료 |
| **시스템 로그** | `debug_output.txt` | `system_logs` 컬렉션 (실시간 stream) | ✅ 완료 |
| **주식 기본 정보** | `stock_infos.csv` | `stock_infos` 컬렉션 | ✅ 완료 |
| **VCP 스캔 결과** | `vcp_results/*.csv` | `vcp_reports` 컬렉션 | ✅ 완료 |

## 기술적 변경 사항 요약

### 1. 백엔드 (Python / Node.js)
- **데이터 기록**: `pb_utils.py`를 통해 모든 파이썬 스크립트가 PocketBase SDK를 사용하여 데이터를 업서트(Upsert)하도록 통합되었습니다.
- **로그 핸들링**: `scriptRunner.ts`가 자식 프로세스의 출력을 캡처하여 PocketBase `system_logs` 컬렉션에 직결 전송합니다.

### 2. 프론트엔드 (Next.js)
- **API 라우트**: `/api/system/*` 및 `/api/portfolio/*` 경로의 모든 API가 `fs` 모듈을 통한 파일 읽기 대신 `PocketBase` SDK와 전용 유틸리티(`fetchFromPB`)를 사용하여 통신합니다.
- **실시간성**: PocketBase의 빠른 조회 성능과 `force-dynamic` 설정을 통해 실시간 데이터의 일관성을 확보했습니다.

## 관리 및 유지보수 가이드
1. **PocketBase 어드민**: `http://localhost:8090/_/` 접속을 통해 모든 데이터를 시각적으로 관리할 수 있습니다.
2. **로그 관리**: `system_logs`에 쌓이는 데이터는 `DELETE /api/system/logs` API를 통해 언제든 비울 수 있습니다.
3. **환경 변수**: `.env` 파일의 `PB_URL`, `PB_EMAIL`, `PB_PASSWORD` 설정을 통해 접속 정보를 통합 관리합니다.

---
*본 마이그레이션을 통해 시스템의 확장성과 데이터 무결성이 획기적으로 향상되었습니다.*
