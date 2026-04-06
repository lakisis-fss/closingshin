import json
import requests

pb_url = "http://127.0.0.1:8090"

def check_vcp_mode():
    try:
        # Fetch portfolio items
        res = requests.get(f"{pb_url}/api/collections/portfolio/records?limit=200")
        if res.status_code != 200:
            print(f"Error: {res.status_code}")
            return
            
        items = res.json().get('items', [])
        
        targets = ['052860', '065530', '200710']
        for item in items:
            ticker = item.get('ticker')
            if ticker in targets:
                print(f"Ticker: {ticker}, Name: {item.get('name')}, vcp_mode: '{item.get('vcp_mode')}'")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_vcp_mode()
