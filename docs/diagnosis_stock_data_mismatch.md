# VCP 대시보드 종목 데이터 불일치 진단 및 해결 리포트

## 1. 현상 요약
일부 종목(예: 미래에셋증권2우B)에서 특정 날짜(2026-04-01)의 종가는 정확히 표시되나, 전일 대비 변화율이 당일(8.43%)이 아닌 전일(3/31, -2.5%) 수치로 오표기되는 현상 발견.

## 2. 근본 원인 분석 (Root Cause)
데이터 소스의 파편화 및 외부 API의 업데이트 지연이 결합된 문제였습니다.

### 데이터 소스 이원화
- **가격 데이터**: `vcp_reports` 컬렉션에서 가져옴. `08_sync_market_data.py`가 네이버 차트 API(`fchart.naver.com`)를 통해 실시간에 가깝게 업데이트함.
- **변화율 데이터**: `stock_infos` 컬렉션에서 가져옴. `06_collect_stock_data.py`가 네이버 모바일 트렌드 API(`m.stock.naver.com`)를 통해 수집함.

### API 지연 이슈
- 네이버 모바일 트렌드 API는 차트 API보다 업데이트가 늦는 경우가 발생함.
- `06_collect_stock_data.py`가 실행될 때 API 응답의 첫 번째 항목(최신 데이터)이 요청한 날짜가 아닌 이전 영업일 데이터였음에도 불구하고 이를 검증 없이 저장함.
- 결과적으로 `stock_infos` 테이블의 4/1 레코드에 3/31 변화율이 잘못 기입됨.

## 3. 해결 내용 (Surgical Fix)

### 프론트엔드: 데이터 소스 정합성 강화
- `types.ts`: `VcpResult` 인터페이스에 `change_pct` 필드 추가.
- `api.ts`: PocketBase 조회 시 `vcp_reports`에서 `change_pct`를 함께 가져오도록 수정.
- `page.tsx`: 변화율 표시 시 `vcp_reports`의 데이터를 최우선으로 사용하고, 없을 경우에만 `stock_infos`를 참조하도록 우선순위 조정.

### 백엔드: 데이터 오염 방지 (Validation)
- `06_collect_stock_data.py`: API가 반환한 데이터의 `bizdate`가 요청한 날짜와 일치하는지 검증하는 로직 추가. 불일치 시 데이터를 저장하지 않고 경고 메시지를 남기도록 수정.

## 4. 향후 재발 방지
- 주요 지표(종가, 변화율)는 가능한 한 동일한 시점에 동일한 소스에서 수집된 데이터를 사용하도록 구조화함.
- 외부 API 의존 로직에 날짜 및 무결성 검증 단계를 필수적으로 포함함.

---
**Tag**: #StockData #VCP #Debugging #PocketBase #NaverFinance
**Date**: 2026-04-01
**Vault**: SSH_2025
