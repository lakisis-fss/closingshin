
import FinanceDataReader as fdr
from datetime import datetime, timedelta

TODAY_DASH = datetime.now().strftime("%Y-%m-%d")
start_dt = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")

print(f"Testing for KOSPI (KS11) from {start_dt} to {TODAY_DASH} using NAVER source")

# Test Naver (FDR)
try:
    df_naver = fdr.DataReader('KS11', start_dt, TODAY_DASH, data_source='naver')
    print("\n[Naver (KS11)]")
    if not df_naver.empty:
        print(df_naver.tail())
    else:
        print("Empty DataFrame")
except Exception as e:
    print(f"Naver Failed: {e}")
