import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

PB_URL = os.getenv("PB_URL", "http://127.0.0.1:8090")
PB_EMAIL = os.getenv("PB_EMAIL")
PB_PASSWORD = os.getenv("PB_PASSWORD")

def check_structure():
    r = requests.post(f"{PB_URL}/api/collections/_superusers/auth-with-password", json={"identity": PB_EMAIL, "password": PB_PASSWORD})
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    url = f"{PB_URL}/api/collections/market_status/records?perPage=1&sort=-date"
    resp = requests.get(url, headers=headers)
    items = resp.json().get("items", [])
    if items:
        data = items[0]['data']
        print(f"Keys: {list(data.keys())}")
        if 'KOSPI' in data:
            print(f"KOSPI: {data['KOSPI']}")
        else:
            print("KOSPI missing")
    else:
        print("Empty")

if __name__ == "__main__":
    check_structure()
