import FinanceDataReader as fdr
from datetime import datetime, timedelta

def test_history():
    start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    print(f"Fetching history from {start_date}...")
    
    try:
        kospi = fdr.DataReader('KS11', start_date)
        print(f"KOSPI raw length: {len(kospi)}")
        if not kospi.empty:
            print(kospi.tail(5))
        
        kosdaq = fdr.DataReader('KQ11', start_date)
        print(f"KOSDAQ raw length: {len(kosdaq)}")
        if not kosdaq.empty:
            print(kosdaq.tail(5))
            
        common_dates = kospi.index.intersection(kosdaq.index).sort_values()
        print(f"Common dates length: {len(common_dates)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_history()
