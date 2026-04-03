import FinanceDataReader as fdr
import pandas as pd

# 전 종목 리스트 확보
print("Fetching all KRX listings...")
krx = fdr.StockListing('KRX')

target_prices = {
    'BATTERY': 16340,
    'IT': 18990,
    'BANK': 16625,
    'SECURITIES': 27908
}

print("\nSearching for stocks matching target prices (within 1% range)...")
for name, target in target_prices.items():
    print(f"\n[{name}] Target: {target:,}")
    # 현재가(Close)가 target과 비슷한 종목 검색
    # StockListing 결과의 'Close'는 현재가 (지연될 수 있음)
    matches = krx[ (krx['Close'] >= target * 0.95) & (krx['Close'] <= target * 1.05) ]
    for idx, row in matches.iterrows():
        # ETF나 주요 섹터 종목 위주로 출력
        if row['Market'] == 'KOSPI' or 'ETF' in row['Name'] or any(kw in row['Name'] for kw in [name, '2차전지', '반도체', '은행', '증권', 'IT', '철강']):
            print(f"  {row['Code']} ({row['Name']}): {row['Close']:,}")
