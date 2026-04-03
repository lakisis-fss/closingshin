# Exit Plan 자동화 청산 시스템 설계

## 개요

현재 Exit Plan은 사용자가 텍스트로 청산 계획을 기록하는 방식입니다. 이를 확장하여 **자동 청산 알람** 및 **청산 트리거 로직**을 구현하려고 합니다.

---

## 청산 조건 분류

### 1. 가격 기반 조건

| 조건명 | 설명 | 예시 | 우선순위 |
|--------|------|------|----------|
| **손절 (Stop Loss)** | 매수가 대비 N% 하락 시 청산 | 매수가 100,000원, -7% = 93,000원 이하 | 필수 |
| **익절 (Take Profit)** | 매수가 대비 N% 상승 시 청산 | 매수가 100,000원, +15% = 115,000원 이상 | 필수 |
| **트레일링 스탑 (Trailing Stop)** | 보유 중 최고가 대비 N% 하락 시 청산 (이익 보존) | 최고가 120,000원, -10% = 108,000원 이하 | 높음 |
| **지지선 이탈** | 특정 가격 또는 이동평균선 하회 시 청산 | 50일 MA 이탈 시 | 중간 |
| **목표가 도달** | 설정한 목표 가격 도달 시 청산 | 130,000원 도달 시 | 중간 |

### 2. 시간 기반 조건

| 조건명 | 설명 | 예시 | 우선순위 |
|--------|------|------|----------|
| **타임컷 (Time Cut)** | 보유 N일 경과 시 무조건 청산 | 30일 보유 후 청산 | 필수 |
| **결산일 청산** | 분기/연말 결산 전 청산 | 12월 20일 전 청산 | 낮음 |
| **이벤트 기반** | 특정 이벤트(실적 발표 등) 전후 청산 | 어닝 발표 1일 전 청산 | 낮음 |

### 3. 기술적 지표 조건

| 조건명 | 설명 | 트리거 기준 | 우선순위 |
|--------|------|-------------|----------|
| **VCP 패턴 붕괴** | VCP 수축 패턴이 깨질 때 | 피벗 포인트 하회 + 거래량 증가 | 높음 |
| **거래량 급등 + 하락** | 대량 거래량과 함께 하락 시 | 평균 거래량 200% + 음봉 | 중간 |
| **52주 신고가 실패** | 돌파 시도 후 음봉 마감 시 | 신고가 근접 후 -3% 하락 | 중간 |
| **이동평균선 이탈** | 주요 MA 하회 시 | 20일/50일 MA 이탈 | 중간 |
| **MACD 데드크로스** | MACD 시그널 하향 돌파 시 | 매도 시그널 발생 | 낮음 |

### 4. 수급 기반 조건

| 조건명 | 설명 | 트리거 기준 | 우선순위 |
|--------|------|-------------|----------|
| **기관/외인 순매도 전환** | N일 연속 순매도 시 | 5일 연속 기관+외인 순매도 | 중간 |
| **공매도 급증** | 공매도 비율 급등 시 | 공매도 비율 10% 초과 | 낮음 |
| **대량 매도 체결** | 시간외 대량매매 매도 발생 시 | 발행주식의 1% 이상 매도 | 낮음 |

### 5. 펀더멘탈/뉴스 조건

| 조건명 | 설명 | 트리거 기준 | 우선순위 |
|--------|------|-------------|----------|
| **실적 발표 후 청산** | 어닝 서프라이즈/쇼크 반응 | 실적 발표 후 -5% 이상 하락 | 낮음 |
| **악재 뉴스 감지** | AI 뉴스 감성 점수 급락 시 | Sentiment Score < -0.5 | 중간 |
| **신용등급 하락** | 기업 신용등급 하향 시 | 등급 1단계 이상 하락 | 낮음 |

### 6. 리스크 관리 조건

| 조건명 | 설명 | 트리거 기준 | 우선순위 |
|--------|------|-------------|----------|
| **포트폴리오 비중 조절** | 단일 종목 비중 N% 초과 시 | 포트폴리오의 25% 초과 | 낮음 |
| **전체 손실 한도** | 포트폴리오 총손실 -N% 시 | 총 자산 -10% 손실 | 중간 |
| **변동성 급등** | 종목 변동성 급격히 증가 시 | ATR 200% 이상 증가 | 낮음 |

---

## 데이터 스키마 설계

### Option A: 단순 규칙 기반 (권장 - Phase 1)

```typescript
interface ExitConditions {
  // 가격 기반 (필수)
  stopLossPercent?: number;      // 예: -7
  takeProfitPercent?: number;    // 예: +15
  trailingStopPercent?: number;  // 예: -10 (고점 대비)
  targetPrice?: number;          // 목표가 (원)
  
  // 시간 기반 (필수)
  timeCutDays?: number;          // 예: 30
  
  // 기술적 지표 (ON/OFF)
  exitOnVcpBreakdown?: boolean;
  exitOnVolumeSpike?: boolean;
  exitOnMaCrossdown?: boolean;
  
  // 수급 기반
  exitOnInstitutionalSellDays?: number; // N일 연속 순매도
  
  // 뉴스 기반
  exitOnNegativeSentiment?: boolean;
  sentimentThreshold?: number;   // 예: -0.5
}
```

### Option B: 유연한 조건 배열 (Phase 2+)

```typescript
type ConditionType = 
  | 'stop_loss' 
  | 'take_profit' 
  | 'trailing_stop'
  | 'time_cut'
  | 'vcp_breakdown'
  | 'volume_spike'
  | 'ma_crossdown'
  | 'institutional_sell'
  | 'negative_sentiment';

type ConditionOperator = 'gte' | 'lte' | 'eq' | 'days_after' | 'consecutive';

type ActionType = 'alert' | 'sell_all' | 'sell_partial' | 'notify_only';

interface ExitCondition {
  id: string;
  type: ConditionType;
  operator: ConditionOperator;
  value: number | boolean;
  action: ActionType;
  sellPercent?: number;       // 부분 청산 시 비율 (예: 50%)
  priority: number;           // 우선순위 (1이 가장 높음)
  enabled: boolean;
  description?: string;       // 사용자 메모
}

interface ExitPlan {
  id: string;
  portfolioItemId: string;
  
  // 프리셋 템플릿
  template?: 'conservative' | 'moderate' | 'aggressive' | 'swing' | 'custom';
  
  // 조건 배열
  conditions: ExitCondition[];
  
  // 복합 조건 로직
  logicOperator: 'AND' | 'OR' | 'FIRST_MATCH';
  
  // 메타데이터
  createdAt: Date;
  updatedAt: Date;
  lastTriggeredAt?: Date;
  triggerHistory: TriggerEvent[];
}

interface TriggerEvent {
  conditionId: string;
  triggeredAt: Date;
  priceAtTrigger: number;
  action: ActionType;
  executed: boolean;
}
```

### Option C: 템플릿 시스템 (Phase 3)

```typescript
const EXIT_TEMPLATES = {
  conservative: {
    name: '보수적 전략',
    description: '손실 최소화, 안정적 수익 추구',
    conditions: {
      stopLossPercent: -5,
      takeProfitPercent: 10,
      timeCutDays: 20,
      exitOnVcpBreakdown: true,
    }
  },
  moderate: {
    name: '균형 전략',
    description: 'VCP 패턴 기반 중기 트레이딩',
    conditions: {
      stopLossPercent: -7,
      takeProfitPercent: 15,
      trailingStopPercent: -10,
      timeCutDays: 30,
      exitOnVcpBreakdown: true,
      exitOnInstitutionalSellDays: 5,
    }
  },
  aggressive: {
    name: '공격적 전략',
    description: '높은 수익 추구, 높은 리스크 감수',
    conditions: {
      stopLossPercent: -10,
      takeProfitPercent: 30,
      trailingStopPercent: -15,
      timeCutDays: 60,
    }
  },
  swing: {
    name: '스윙 트레이딩',
    description: '단기~중기 스윙 매매',
    conditions: {
      stopLossPercent: -7,
      takeProfitPercent: 15,
      trailingStopPercent: -10,
      timeCutDays: 30,
      exitOnVolumeSpike: true,
    }
  }
};
```

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
├─────────────────────────────────────────────────────────────┤
│  Portfolio Page                                              │
│  ├── AddStockModal (Exit Plan 설정)                          │
│  ├── PositionCard (현재 조건 상태 표시)                        │
│  └── AlertPanel (트리거된 알림 표시)                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend (Python)                         │
├─────────────────────────────────────────────────────────────┤
│  exit_monitor.py                                             │
│  ├── ConditionChecker                                        │
│  │   ├── check_price_conditions()                            │
│  │   ├── check_time_conditions()                             │
│  │   ├── check_technical_conditions()                        │
│  │   └── check_supply_conditions()                           │
│  │                                                           │
│  └── AlertDispatcher                                         │
│      ├── send_push_notification()                            │
│      ├── send_email_alert()                                  │
│      └── log_trigger_event()                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Scheduler (APScheduler)                  │
├─────────────────────────────────────────────────────────────┤
│  장중 조건 체크: 매 10분                                       │
│  장마감 후 정산: 매일 18:00                                    │
│  일간 리포트: 매일 20:00                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Sources                             │
├─────────────────────────────────────────────────────────────┤
│  실시간 시세: pykrx / 증권사 API                               │
│  수급 데이터: stock_info CSV                                  │
│  뉴스 감성: news_analysis CSV                                 │
│  VCP 상태: vcp_report CSV                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 구현 로드맵

### Phase 1: 기본 조건 필드화 (1주)

**목표**: 손절/익절/타임컷 조건을 구조화된 필드로 저장

**작업 내용**:
1. `PortfolioItem` 인터페이스에 `exitConditions` 필드 추가
2. `AddStockModal`에 조건 입력 UI 추가
3. 포트폴리오 카드에 조건 상태 표시
4. localStorage 저장 구조 업데이트

**산출물**:
- 수정된 타입 정의
- 조건 입력 폼 컴포넌트
- 조건 표시 UI

---

### Phase 2: 조건 모니터링 + 알림 (1-2주)

**목표**: 조건 충족 시 알림 발송

**작업 내용**:
1. Python 스케줄러로 주기적 조건 체크
2. 웹 푸시 알림 구현
3. 알림 히스토리 저장
4. 알림 설정 페이지

**산출물**:
- `exit_monitor.py` 스크립트
- 알림 시스템 (웹 푸시 / 텔레그램)
- 알림 대시보드

---

### Phase 3: 템플릿 + 트레일링 스탑 (1주)

**목표**: 프리셋 전략과 고급 조건 지원

**작업 내용**:
1. 템플릿 선택 UI
2. 트레일링 스탑 로직 구현 (고점 추적)
3. 조건 편집 모달
4. 백테스트 시뮬레이터 (선택)

**산출물**:
- 템플릿 시스템
- 트레일링 스탑 계산기
- 전략 비교 UI

---

### Phase 4: 고급 조건 (2주)

**목표**: 기술적/수급/뉴스 기반 조건 지원

**작업 내용**:
1. VCP 패턴 붕괴 감지 로직
2. 수급 데이터 연동
3. 뉴스 감성 점수 모니터링
4. 복합 조건 (AND/OR) 지원

**산출물**:
- 고급 조건 체커
- 조건 조합 빌더 UI
- 조건별 통계/분석

---

### Phase 5: 자동 청산 트리거 (별도)

**목표**: 증권사 API 연동으로 실제 주문 실행

**작업 내용**:
1. 증권사 API 연동 (키움, 이베스트 등)
2. 주문 실행 모듈
3. 안전장치 (확인 절차, 한도 설정)
4. 거래 로그 및 리포트

**주의사항**:
- 증권사 API 사용 조건 확인 필요
- 자동매매 관련 법적 검토
- 테스트 환경에서 충분한 검증 필수

---

## UI/UX 설계 방향

### AddStockModal 확장

```
┌─────────────────────────────────────────────┐
│ EXIT PLAN                                    │
├─────────────────────────────────────────────┤
│ [템플릿 선택] ▼ 균형 전략                     │
├─────────────────────────────────────────────┤
│                                              │
│ ┌─ 가격 조건 ──────────────────────────────┐ │
│ │ 손절        [  -7  ] %                   │ │
│ │ 익절        [ +15  ] %                   │ │
│ │ 트레일링    [ -10  ] % (고점 대비)        │ │
│ └──────────────────────────────────────────┘ │
│                                              │
│ ┌─ 시간 조건 ──────────────────────────────┐ │
│ │ 타임컷      [  30  ] 일                  │ │
│ └──────────────────────────────────────────┘ │
│                                              │
│ ┌─ 기술적 조건 (선택) ─────────────────────┐ │
│ │ ☑ VCP 패턴 붕괴 시 청산                   │ │
│ │ ☐ 거래량 급등 + 하락 시 경고              │ │
│ │ ☐ 50일 MA 이탈 시 경고                   │ │
│ └──────────────────────────────────────────┘ │
│                                              │
│ ┌─ 알림 설정 ──────────────────────────────┐ │
│ │ ☑ 조건 충족 시 푸시 알림                  │ │
│ │ ☐ 일간 상태 리포트                        │ │
│ └──────────────────────────────────────────┘ │
│                                              │
│           [ ADD TO PORTFOLIO ]               │
└─────────────────────────────────────────────┘
```

---

## 권장 사항

1. **Phase 1부터 시작**: 복잡한 조건보다 기본 조건(손절/익절/타임컷)부터 안정적으로 구현
2. **알림 우선**: 자동 청산보다 알림 시스템을 먼저 구축하여 사용자가 판단할 수 있게 함
3. **VCP 특화**: 일반적인 조건보다 VCP 패턴에 최적화된 조건 우선 개발
4. **백테스트**: 조건 설정 전 과거 데이터로 시뮬레이션 기능 제공 고려

---

## 참고 자료

- Mark Minervini의 SEPA 전략 청산 규칙
- William O'Neil의 CAN SLIM 손절 원칙
- VCP 패턴 붕괴 판단 기준
