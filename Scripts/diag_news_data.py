import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import sys

# Windows Console Encoding Fix
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(dotenv_path=env_path)

PB_URL = os.getenv("PB_URL", "http://127.0.0.1:8090")
PB_EMAIL = os.getenv("PB_EMAIL")
PB_PASSWORD = os.getenv("PB_PASSWORD")

def get_token():
    try:
        resp = requests.post(f"{PB_URL}/api/admins/auth-with-password", 
                           json={"identity": PB_EMAIL, "password": PB_PASSWORD})
        return resp.json().get("token")
    except:
        return None

def check_collection(collection, date_str):
    token = get_token()
    if not token:
        print("Auth failed")
        return
    
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    # Try both strict and loose filter
    headers = {"Authorization": token}
    filter_str = f'date ~ "{formatted_date}"'
    
    url = f"{PB_URL}/api/collections/{collection}/records?filter={filter_str}&limit=5"
    resp = requests.get(url, headers=headers)
    data = resp.json()
    
    print(f"\n--- [Diag: {collection}] ---")
    print(f"Filter: {filter_str}")
    print(f"Total Items: {data.get('totalItems', 0)}")
    
    if data.get('items'):
        item = data['items'][0]
        print(f"Sample Item Keys: {list(item.keys())}")
        print(f"Sample Item Data (subset):")
        print(f"  ID: {item.get('id')}")
        print(f"  Date: {item.get('date')}")
        print(f"  Ticker/Code: {item.get('ticker') or item.get('code') or 'MISSING'}")
        print(f"  Name: {item.get('name') or item.get('target_stock') or 'MISSING'}")
        
        # Check specific ticker for 036170
        ticker_filter = f'ticker ~ "036170" || code ~ "036170"'
        url_ticker = f"{PB_URL}/api/collections/{collection}/records?filter={ticker_filter}&limit=1"
        resp_t = requests.get(url_ticker, headers=headers)
        data_t = resp_t.json()
        if data_t.get('items'):
            print(f"Ticker 036170 check: FOUND")
            print(f"  Actual fields: Ticker={data_t['items'][0].get('ticker')}, Code={data_t['items'][0].get('code')}")
        else:
            print(f"Ticker 036170 check: NOT FOUND in this collection")

if __name__ == "__main__":
    date = "20260327" # Sample date from user screenshot usually
    # Finding latest scan date
    check_collection("news_reports", date)
    check_collection("news_analysis", date)
