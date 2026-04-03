import FinanceDataReader as fdr
import sys

try:
    df = fdr.DataReader('020000', '2026-03-01')
    print("Historical Closing Prices for 020000 (한섬):")
    for index, row in df.iterrows():
        print(f"  {index.strftime('%Y-%m-%d')}: {int(row['Close'])}")
except Exception as e:
    print(f"Error: {e}")
