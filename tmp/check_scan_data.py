import requests
import json

def find_missing_mode():
    url = "http://127.0.0.1:8090/api/collections/vcp_reports/records?limit=200&sort=-date"
    r = requests.get(url)
    items = r.json().get('items', [])
    
    # Check for specific stocks in recent scans
    for i in items:
        if i['ticker'] in ['052860', '065530', '200710']:
            print(f"Date: {i['date']}, Ticker: {i['ticker']}, Name: {i['name']}, Mode: '{i.get('vcp_mode')}', Score: {i.get('vcp_score')}")

if __name__ == "__main__":
    find_missing_mode()
