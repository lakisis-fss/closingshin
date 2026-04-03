# 시장 데이터 실시간 동기화 프로세스 시각화

```mermaid
graph TD
    A[Scheduler 시작] --> B{지금이 장 중인가?}
    B -- "Yes (09:00 - 15:40)" --> C[네이버 금융 실시간 크롤링]
    B -- "No" --> D[FinanceDataReader 과거 데이터 조회]
    
    C --> E[실시간 가격 & 등락 포인트 추출]
    D --> F{데이터가 오늘 날짜인가?}
    F -- "No (지연됨)" --> C
    F -- "Yes" --> G[데이터 확정]
    
    E --> G
    G --> H[섹터 ETF 실시간 보정]
    H --> I[히스토리 차트에 오늘 데이터 주입]
    I --> J[JSON 파일 저장 & 대시보드 반영]
    
    subgraph "Karpathy Style Optimization"
    E
    I
    end
```

## 현재 상태 (Status Board)
- **KOSPI/KOSDAQ**: 실시간 완료 (Naver Scraper)
- **Sector ETFs**: 실시간 완료 (Naver Scraper)
- **Trend Chart**: 오늘 데이터 포함 완료 (Dynamic Injection)
- **AI Insight**: 실시간 데이터 기반 생성 완료
