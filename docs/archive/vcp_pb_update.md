# VCP 스캔 데이터 소스 업데이트 (PocketBase 통합)

## 1. 개요
기존에 로컬 CSV 파일 및 KIND API에 의존하던 VCP 스캔 스크립트(`02_scan_vcp.py`)가 PocketBase의 `stock_infos` 및 `ohlcv` 컬렉션을 참조하도록 업데이트되었습니다. 이를 통해 데이터 관리의 중앙 집중화와 안정성을 확보했습니다.

## 2. 주요 변경 사항

### 2.1. 종목 리스트 수집 방식 변경
- **기존**: KIND API (`https://kind.krx.co.kr/...`)를 통해 매번 시장별로 종목 리스트를 다운로드.
- **변경**: PocketBase의 `stock_infos` 컬렉션에서 전체 종목 리스트를 한 번에 가져오도록 수정. 
  - `pb_utils.query_pb` 기능을 강화하여 500개 이상의 레코드(전체 약 2600개)도 `get_full_list`를 통해 효율적으로 가져옵니다.

### 2.2. 주가 데이터(OHLCV) 수집 및 Fallback 구현
- **기존**: 로컬 `Scripts/data/prices/*.csv` 파일 참조.
- **변경**: PocketBase의 `ohlcv` 컬렉션을 우선적으로 참조.
  - 만약 PocketBase에 데이터가 없거나 5거래일 미만으로 부족할 경우, **로컬 CSV 파일에서 데이터를 읽어오는 Fallback 로직**을 추가하여 "No data collected" 에러 발생 가능성을 최소화했습니다.
  - 날짜 형식(YYYYMMDD vs YYYY-MM-DD)을 PocketBase 필터 형식에 맞게 자동 정규화(`normalize_date`) 하도록 개선했습니다.

### 2.3. 병렬 처리 및 성능 최적화
- `ThreadPoolExecutor`를 활용하여 수백 개의 종목에 대한 주가 데이터를 병렬로 조회함으로써 스캔 속도를 개선했습니다.
- 불필요한 중복 코드와 사용되지 않는 함수(`fetch_and_calculate_momentum` 등)를 정리하고 `_fetch_ohlcv_for_target`으로 통합했습니다.

## 3. 발생했던 문제 및 해결 방법
- **0원 주가 문제**: `ohlcv` 컬렉션의 데이터가 불완전하거나 필드 추출 시 SDK 객체 변환 오류로 인해 발생했습니다. 
  - `pb_utils.py`에서 레코드 데이터를 딕셔너리로 변환할 때 `__dict__` 대신 속성 접근 방식을 사용하여 모든 필드(`open`, `close` 등)가 정확히 추출되도록 수정했습니다.
- **수집 데이터 없음 에러**: PocketBase 데이터가 아직 완전히 동기화되지 않은 상태에서 발생했습니다.
  - CSV Fallback 모드를 도입하여 PB 데이터가 부족해도 기존 로컬 데이터를 활용해 분석을 진행할 수 있도록 조치했습니다.

## 4. 향후 작업 권장
- 로컬 CSV에만 존재하는 과거 주가 데이터를 `ohlcv` 컬렉션으로 완전히 마이그레이션(`pb_prices_migration.py` 활용)하는 것을 추천합니다.
- 동기화 스크립트(`08_sync_market_data.py`)가 정기적으로 실행되도록 스케줄러를 확인하십시오.
