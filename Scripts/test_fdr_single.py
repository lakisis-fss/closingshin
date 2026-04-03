import FinanceDataReader as fdr
from datetime import datetime

def test_fdr_single():
    print("Testing FDR single ticker fetch...")
    try:
        # 삼성전자 (005930)
        ticker = '005930'
        start_date = '2026-03-01'
        end_date = '2026-03-05'
        
        print(f"Fetching {ticker} from {start_date} to {end_date} via FDR...")
        df = fdr.DataReader(ticker, start_date, end_date)
        
        if df is not None and not df.empty:
            print("Success: FDR single ticker fetch worked!")
            print(df.tail(2))
        else:
            print("Error: FDR DataFrame is empty")
            
    except Exception as e:
        print(f"FDR Single Fetch Failed: {e}")

if __name__ == "__main__":
    test_fdr_single()
