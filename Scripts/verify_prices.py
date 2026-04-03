import pb_utils
import FinanceDataReader as fdr
import sys

# Windows Console Encoding Fix
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

tickers = ["020000", "420770"]
for t in tickers:
    price = pb_utils.get_synchronized_price(t)
    print(f"Ticker: {t}, Synchronized Price: {price}")
    
    # Check FDR directly
    try:
        df = fdr.DataReader(t)
        if not df.empty:
            last_close = df.iloc[-1]['Close']
            print(f"  FDR Last Close: {last_close} (Date: {df.index[-1]})")
    except:
        print(f"  FDR Fetch Failed for {t}")
