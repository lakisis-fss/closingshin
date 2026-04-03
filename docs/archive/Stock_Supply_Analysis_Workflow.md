# 개별 종목 수급 분석 워크플로우 (누적 데이터 수집)

개별 종목의 **기관, 외국인, 개인 투자자**들의 수급 현황을 **5일, 15일, 30일, 50일, 100일** 단위로 누적하여 분석하기 위한 자동화 계획입니다. `pykrx` 라이브러리를 활용하여 효율적으로 데이터를 수집하고 가공하는 절차를 설명합니다.

---

## 1. 분석 목표 (Goal)
*   **대상:** 사용자가 지정한 종목 (예: 삼성전자 `005930`)
*   **핵심 지표:** 투자자별(기관, 외국인, 개인) **순매수 거래대금**의 기간별 누적 합계
*   **분석 기간:** 단기(5일)부터 중장기(100일)까지의 수급 주체별 포지션 변화 파악

## 2. 상세 워크플로우 (Step-by-Step)

### Step 1: 환경 설정 및 타겟 선정
*   **라이브러리:** `pykrx` (데이터 수집), `pandas` (데이터 가공), `datetime` (날짜 계산)
*   **입력값:** 종목 코드 (Ticker), 기준일 (오늘)

### Step 2: 데이터 수집 (Batch Fetching)
서버 과부하를 막고 속도를 높이기 위해 기간별로 5번 요청하지 않고, **한 번에 긴 데이터를 가져와서 자르는 방식**을 사용합니다.

*   **전략:** '100거래일' 데이터를 확보하기 위해, 달력 기준으로는 약 6개월(180일) 전부터 오늘까지의 일별 데이터를 한 번에 요청합니다.
*   **함수:** `stock.get_market_trading_value_by_date(start_date, end_date, ticker)`

### Step 3: 데이터 전처리 (Preprocessing)
1.  **정렬:** 수집된 데이터를 날짜 기준 **내림차순(최신 날짜가 위로)**으로 정렬합니다.
2.  **슬라이싱(Slicing):** 영업일 기준으로 정확한 기간을 잘라냅니다.
    *   예) 5일 누적 = 위에서부터 5개 행(`row`) 선택
3.  **집계(Aggregation):** 잘라낸 데이터에서 '기관합계', '외국인', '개인' 컬럼의 값을 모두 더합니다(`sum`).

### Step 4: 결과 통합 및 시각화
*   계산된 5개 기간(5, 15, 30, 50, 100일)의 데이터를 하나의 표(DataFrame)로 합칩니다.
*   금액 단위가 크므로 '억 원' 단위 등으로 변환하여 가독성을 높입니다.

---

## 3. 파이썬 구현 코드 (Example)

```python
from pykrx import stock
from datetime import datetime, timedelta
import pandas as pd

def get_cumulative_investor_trend(ticker):
    # 1. 날짜 설정 (100거래일 확보를 위해 넉넉히 180일 전부터 조회)
    today = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=180)).strftime("%Y%m%d")
    
    # 2. 일별 데이터 한 번에 가져오기
    # 기관, 외국인, 개인의 순매수 금액 데이터
    df = stock.get_market_trading_value_by_date(start_date, today, ticker)
    
    # 3. 최신 날짜순으로 정렬 (내림차순)
    df = df.sort_index(ascending=False)
    
    # 4. 기간별 누적 합계 계산
    periods = [5, 15, 30, 50, 100]
    result_data = {}
    
    for p in periods:
        # 최근 p일치 데이터 자르기
        subset = df.iloc[:p]
        
        # 투자자별 합계 계산 (단위: 억 원으로 변환 예시)
        # 100,000,000으로 나누어 억 단위 표기
        sums = subset[['기관합계', '외국인', '개인']].sum() / 100000000
        result_data[f'{p}일'] = sums
        
    # 5. 결과 반환 (DataFrame 변환)
    result_df = pd.DataFrame(result_data).T # 행/열 전환
    return result_df

# 실행 예시 (삼성전자)
print(get_cumulative_investor_trend("005930"))
```

## 4. 활용 팁 (Interpretation)
*   **외국인/기관 동반 매수:** 5일, 15일 등 단기 누적에서 외국인과 기관이 동시에 '빨간불(순매수)'이라면 주가 상승 확률이 높습니다. (양매수)
*   **손바뀜 포착:** 100일 누적은 개인이 매수 우위인데, 최근 5일, 15일 누적에서 외국인 매수로 전환되었다면 중요한 변곡점일 수 있습니다.
