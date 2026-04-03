from pykrx import stock
from datetime import datetime

def test_pykrx_single():
    print("Testing pykrx single ticker fetch (Naver backend check)...")
    try:
        # 삼성전자 (005930)
        ticker = '005930'
        start_date = '20260301'
        end_date = '20260305'
        
        print(f"Fetching {ticker} from {start_date} to {end_date}...")
        df = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
        
        if df is not None and not df.empty:
            print("Success: pykrx single ticker fetch worked!")
            print(df.tail(2))
        else:
            print("Error: DataFrame is empty")
            
    except Exception as e:
        print(f"pykrx Single Fetch Failed: {e}")

if __name__ == "__main__":
    test_pykrx_single()
