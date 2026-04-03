# 07. 데이터 수집 파이프라인 가이드 (Data Collection)

이 문서는 ClosingSHIN 시스템이 거시경제, 종목 수급 및 뉴스 데이터를 수집하고 분석하는 파이프라인 구조와 각 스크립트의 역할을 설명합니다.

---

## 1. 시장 상태 진단 (`05_collect_market_status.py`)

주식시장의 현재 상태를 파악하기 위해 거시경제 지표와 시장 수급을 매일 수집합니다.

- **실행 주기:** 매 10분마다 스케줄러 자동 실행 (또는 Admin 페이지에서 수동 실행)
- **데이터 소스:** `FinanceDataReader` (환율, 국채 금리, 유가, 글로벌 지수) + 네이버 크롤링 (투자자별 매매, 수급)
- **수집 지표:**
  - **Macro (거시):** 원/달러 환율, 미 10년물 국채 금리, WTI 원유
  - **Supply & Demand (수급):** 투자자별(외인/기관/개인) 순매수, 고객 예탁금, 신용융자 잔고
  - **Technical (기술적):** ADR (등락비율 - 120% 과열, 80% 바닥), VKOSPI (공포지수)
  - **Sectors (섹터):** KOSPI200 및 반도체, 2차전지 등 주요 7개 섹터 ETF 수익률
- **저장:** PocketBase `market_status` 컬렉션 (날짜별) + `settings` 컬렉션 (최신 시황 미러링)

---

## 2. 펀더멘털 & 수급 누적 분석 (`06_collect_stock_data.py`)

VCP 스캔 결과로 선정된 관심 종목들의 깊이 있는 재무 상태와 수급 주체를 파악합니다.

- **기능:** VCP 스캔 또는 뉴스 분석이 완료된 종목 리스트의 재무 지표와 외인/기관 연속 매수 동향을 수집합니다.
- **데이터 소스:** 네이버 주식 페이지 크롤링
- **수집 지표:**
  - **펀더멘털:** PER (주가수익비율), PBR (주가순자산비율), EPS, BPS
  - **수급 (누적):** 최근 5일, 15일, 30일, 50일, 100일간의 기관/외국인/개인 누적 순매수 대금(억 원)
- **분석법:** `기관_5일`, `외인_5일` 동반 양수(+)일 경우 강력한 단기 쌍끌이 매수세로 간주합니다.
- **저장:** PocketBase `stock_infos` 컬렉션

---

## 3. 뉴스 수집 및 AI 감성 분석

VCP 패턴이 감지된 종목의 최근 이슈를 수집하고, LLM(Gemini API)를 활용해 투자 관점의 감성 분석을 수행합니다.

### 3-1. 뉴스 수집 (`04_collect_news.py`)
- Naver Search API를 통해 최근 7일 내 관련 뉴스를 수집합니다.
- `difflib`을 이용한 유사 제목 중복 기사 제거 및 언론사 신뢰도 가중치를 부여합니다.
- API로 부족한 경우 네이버 웹 검색 크롤링으로 자동 전환합니다 (하이브리드 방식, 상세: `04_News_Collector.md` 참조).
- **저장:** PocketBase `news_reports` 컬렉션

### 3-2. AI 감성 분석 (`05_analyze_news.py`)
- 수집된 뉴스 기사를 Gemini 2.0 Flash 모델에 전송하여 정형화된 JSON 형태로 심층 분석합니다.
- **분석 항목 (5 Core Outputs):**
  1. **감정 점수 (Sentiment Score):** `-1.0`(최악) ~ `0`(중립) ~ `+1.0`(최고)
  2. **영향력 강도 (Impact Intensity):** `Low`, `Medium`, `High`, `Critical`
  3. **지속성 (Time Horizon):** `Short-term`, `Mid-term`, `Long-term`
  4. **뉴스 유형 (Type):** `Fact/공시`, `Earnings`, `Rumor/기대감`
  5. **핵심 테마 (Key Drivers):** 연관 섹터 및 키워드
- **저장:** PocketBase `news_analysis` 컬렉션

---

## 4. 주가 데이터 동기화 (`08_sync_market_data.py`)

VCP 스캔에 사용되는 일봉(OHLCV) 데이터를 PocketBase에 동기화합니다.

- **소스:** `FinanceDataReader`
- **저장:** PocketBase `ohlcv` 컬렉션
- **조회:** `pb_utils.fetch_pb_ohlcv(ticker, start_date, end_date)` 함수로 DataFrame 형태로 반환
