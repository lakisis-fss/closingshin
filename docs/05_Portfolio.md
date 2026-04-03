# 05. 포트폴리오 관리 (Portfolio Management)

이 문서는 ClosingSHIN 대시보드의 포트폴리오(My Portfolio) 기능에 적용된 데이터 관리 아키텍처와 실시간 가격 동기화 로직을 설명합니다.

---

## 1. 포트폴리오 컨셉: "Smart Shield & Spear"
단순한 보유 종목 조회를 넘어, VCP 시스템과 데이터 파이프라인이 결합된 **투자 결정 보조 도구**입니다.

- **방패 (Risk Management):** 펀더멘털 점수, VCP 상태 훼손, 뉴스 감성 악화 시 시각적으로 경고하여 리스크 관리를 돕습니다.
- **창 (Profit Maximization):** VCP 돌파 조건 충족(Action Bar: GO), 수급 급증 시 추가 매수/홀딩의 근거를 제공합니다.

---

## 2. 서버 중심 데이터 관리 아키텍처

### 2-1. Single Source of Truth
모든 포트폴리오 데이터의 원본은 **PocketBase `portfolio` 컬렉션**입니다.
- 사용자가 다른 브라우저, 다른 기기(NAS 배포 환경 포함)에서 접속해도 동일한 데이터를 조회/수정할 수 있습니다.
- 프론트엔드의 상태 관리(Zustand)는 `persist`(로컬 캐싱) 기능 없이, 순수하게 서버 API의 응답을 받아 UI를 그리는 역할만 수행합니다.

### 2-2. API 연동 흐름
- **읽기:** 앱 진입 시 `GET /api/portfolio` -> PocketBase `portfolio` 컬렉션 조회
- **쓰기:** 종목 추가/수정/삭제 시 `POST/PUT/DELETE /api/portfolio` -> PocketBase 직접 수정

---

## 3. 실시간 현재가 동기화 및 표시 로직

백엔드가 주기적으로 수집하는 최신 시장 가격과 사용자가 관리하는 포트폴리오 데이터를 안전하게 병합(Merge)하여 보여줍니다.

### 3-1. 가격 조회 우선순위 (`pb_utils.get_synchronized_price()`)
1. **장중:** 네이버 폴링 API 실시간 현재가 (최우선)
2. **PB ohlcv 컬렉션:** 가장 최신 종가
3. **장외:** 네이버 폴링 API 재시도
4. **PB stock_infos 컬렉션:** 기본 종가
5. **FinanceDataReader:** 최종 폴백

### 3-2. 동기화 프로세스 (`07_calc_portfolio.py`)
- 스케줄러가 10분마다 시장 데이터 업데이트 후 자동 트리거됩니다.
- 시뮬레이션 상태가 `OPEN`인 종목에 대해서만 최신 현재가를 조회합니다.
- 수집된 최신 가격과 수익률 정보를 PocketBase `settings` 컬렉션(`portfolio_status` 키)에 저장합니다.

### 3-3. 프론트엔드 표시 로직 (`HoldingsTable.tsx`)
UI에서는 종목의 시뮬레이션 진행 상태(`simulation.status`)에 따라 다른 가격을 보여줍니다.

- **진행 중 (ACTIVE / OPEN):**
  - 스케줄러가 수집한 **최신 현재가(`currentPrice`)**를 우선 표시하여 실시간 등락률과 평가 손익을 계산합니다.
- **청산 완료 (CLOSED / EXIT):**
  - 과거 종료 시점의 가격인 **종료가(`simulation.exitPrice`)**를 고정해서 표시합니다.
  - 확정 수익(`REALIZED`) 라벨을 부여하여 진행 중인 종목과 시각적으로 구분합니다.

---

## 4. 수동 청산 기능
포트폴리오 대시보드에서 상태가 `OPEN`인 종목에 대해 수동 청산이 가능합니다.
- 청산 모달에서 청산 날짜와 가격을 입력하면 해당 날짜의 고가-저가 범위 내인지 검증합니다.
- 검증 통과 시 `simulation.status`가 `CLOSED`로 변경되고 `exitDate`, `exitPrice`가 기록됩니다.

---

## 5. 자동 청산 시뮬레이션 (`exit_monitor.py`)
- 장중(평일 09:00~15:30) 10분 간격으로 보유 종목의 현재가를 체크합니다.
- 설정된 손절/익절/타임컷 조건 충족 시 데스크탑 알림을 발송합니다.

> **Troubleshooting:**
> 포트폴리오의 가격이 업데이트되지 않거나 0으로 표시될 경우, Admin 페이지의 `Scheduler Status`에서 `Market Data Update` 작업이 정상적으로 동작하고 있는지 가장 먼저 확인해야 합니다.
