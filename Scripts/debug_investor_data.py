from pykrx import stock
from datetime import datetime

today = datetime.now().strftime("%Y%m%d")
print(f"Testing for date: {today}")

try:
    print("\n--- detail=True ---")
    df_detail = stock.get_market_trading_value_by_date(today, today, "KOSPI", detail=True)
    print("Columns:", df_detail.columns.tolist())
    
    print("\n--- detail=False ---")
    df_summary = stock.get_market_trading_value_by_date(today, today, "KOSPI", detail=False)
    print("Columns:", df_summary.columns.tolist())
    
    if '기관합계' in df_summary.columns:
        print("\n'기관합계' found in Summary mode.")
    else:
        print("\n'기관합계' NOT found in Summary mode.")

except Exception as e:
    print("Error:", e)
