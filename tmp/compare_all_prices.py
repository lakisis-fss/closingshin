import FinanceDataReader as fdr
import os
from pocketbase import PocketBase

pb = PocketBase('http://127.0.0.1:8090')
tickers = ['006800', '420770', '020000', '005930']
iso_date = "2026-03-19 00:00:00.000Z"

print(f"{'Ticker':<10} | {'3/19 Close (FDR)':<15} | {'3/19 Close (PB)':<15} | {'3/20 Close (FDR)':<15}")
print("-" * 65)

for t in tickers:
    try:
        df = fdr.DataReader(t, '2026-03-18', '2026-03-20')
        fdr_19 = int(df.loc['2026-03-19', 'Close']) if '2026-03-19' in df.index else "N/A"
        fdr_20 = int(df.loc['2026-03-20', 'Close']) if '2026-03-20' in df.index else "N/A"
        
        # Check PB stock_infos
        r = pb.collection('stock_infos').get_list(1, 1, {
            "filter": f'ticker = "{t}" && date = "{iso_date}"'
        })
        pb_19 = int(r.items[0].close) if r.items else "N/A"
        
        print(f"{t:<10} | {fdr_19:<15} | {pb_19:<15} | {fdr_20:<15}")
        
    except Exception as e:
        print(f"{t:<10} | Error: {e}")
