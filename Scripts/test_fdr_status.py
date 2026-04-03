
import FinanceDataReader as fdr
from datetime import datetime, timedelta

TODAY_DASH = datetime.now().strftime("%Y-%m-%d")
start_dt = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")

print(f"Testing for KOSPI (^KS11) from {start_dt} to {TODAY_DASH}")

# Test Yahoo
try:
    df_yahoo = fdr.DataReader('^KS11', start_dt, TODAY_DASH)
    print("\n[Yahoo (^KS11)]")
    if not df_yahoo.empty:
        print(df_yahoo.tail())
    else:
        print("Empty DataFrame")
except Exception as e:
    print(f"Yahoo Failed: {e}")

# Test KRX (FDR)
try:
    df_krx = fdr.DataReader('KS11', start_dt, TODAY_DASH)
    print("\n[KRX (KS11)]")
    if not df_krx.empty:
        print(df_krx.tail())
    else:
        print("Empty DataFrame")
except Exception as e:
    print(f"KRX Failed: {e}")
