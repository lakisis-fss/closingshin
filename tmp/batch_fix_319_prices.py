import FinanceDataReader as fdr
from pocketbase import PocketBase
import os
from datetime import datetime

pb = PocketBase('http://127.0.0.1:8090')
iso_date = "2026-03-19 00:00:00.000Z"

print(f"Starting batch fix for date: {iso_date}")

try:
    # 1. Get all stock_infos records for that date
    r = pb.collection('stock_infos').get_full_list(query_params={
        "filter": f'date = "{iso_date}"'
    })
    
    print(f"Found {len(r)} records to check.")
    
    for item in r:
        ticker = str(item.ticker).zfill(6)
        try:
            # Fetch correct price from FDR
            df = fdr.DataReader(ticker, '2026-03-19', '2026-03-19')
            if not df.empty and 'Close' in df.columns:
                correct_price = int(df.loc['2026-03-19', 'Close'])
                if int(item.close) != correct_price:
                    print(f"  Fixing {ticker}: {item.close} -> {correct_price}")
                    pb.collection('stock_infos').update(item.id, {"close": correct_price})
                else:
                    # Skip if already correct
                    pass
        except Exception as e:
            print(f"  Failed for {ticker}: {e}")

    print("Batch fix completed.")

except Exception as e:
    print(f"Error during batch fix: {e}")
