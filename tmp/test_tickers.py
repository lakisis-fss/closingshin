import FinanceDataReader as fdr
import pandas as pd

# 유력한 후보군 (KODEX, TIGER 등)
candidates = {
    'KOSPI200': ['069500', '226490', '102110', '114800'], # KODEX 200, KODEX 200TR, TIGER 200, KODEX 인버스 등
    'SEMICON': ['091160', '139230', '462900'],           # KODEX 반도체, TIGER 반도체, TIGER AI반도체 등
    'BATTERY': ['305540', '364980', '394670'],           # KODEX 2차전지, TIGER 2차전지, TIGER 차세대2차전지 등
    'AUTO': ['091170', '139220'],                        # KODEX 자동차, TIGER 현대차그룹+ 등
    'IT': ['139260', '091160'],                          # TIGER 200 IT, KODEX 반도체 등
    'BANK': ['091180', '157450'],                        # KODEX 은행, TIGER 은행 등
    'STEEL': ['117680', '139250'],                       # KODEX 철강, TIGER 200 철강 등
    'SECURITIES': ['091190', '159800']                  # KODEX 증권, TIGER 증권 등
}

print("Searching for matching values...")
for name, tickers in candidates.items():
    print(f"\n[{name}]")
    for t in tickers:
        try:
            df = fdr.DataReader(t)
            if not df.empty:
                last_price = df.iloc[-1]['Close']
                print(f"  {t}: {last_price:,.0f}")
        except:
            pass
