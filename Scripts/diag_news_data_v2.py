import os
import json
import sys
# Add current directory to path if needed to find pb_utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pb_utils

# Windows Console Encoding Fix
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def check_collection(collection, date_str):
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    filter_str = f'date ~ "{formatted_date}"'
    
    print(f"\n--- [Diag: {collection}] ---")
    print(f"Filter: {filter_str}")
    
    try:
        data = pb_utils.query_pb(collection, filter_str=filter_str, limit=5)
        print(f"Items found with date filter: {len(data)}")
        
        if data:
            item = data[0]
            print(f"Sample Item (fields): {list(item.keys())}")
            print(f"  Ticker: {item.get('ticker')}")
            print(f"  Code: {item.get('code')}")
            print(f"  Name: {item.get('name')}")
            print(f"  Target Stock: {item.get('target_stock')}")
            print(f"  Date Value: '{item.get('date')}'")

        # Specific Ticker Check for 036170
        ticker_val = "036170"
        t_filter = f'ticker ~ "{ticker_val}" || code ~ "{ticker_val}"'
        data_t = pb_utils.query_pb(collection, filter_str=t_filter, limit=1)
        if data_t:
            it = data_t[0]
            print(f"Ticker {ticker_val} found!")
            print(f"  Actual fields -> Ticker: '{it.get('ticker')}', Code: '{it.get('code')}', Date: '{it.get('date')}'")
        else:
            print(f"Ticker {ticker_val} NOT FOUND in '{collection}'")
            
    except Exception as e:
        print(f"Error checking {collection}: {e}")

if __name__ == "__main__":
    # Check for the date in the user's screenshot
    target_date = "20260327" 
    check_collection("news_reports", target_date)
    check_collection("news_analysis", target_date)
