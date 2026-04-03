import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

PB_URL = os.getenv("PB_URL", "http://127.0.0.1:8090")
PB_EMAIL = os.getenv("PB_EMAIL")
PB_PASSWORD = os.getenv("PB_PASSWORD")

def check_latest():
    r = requests.post(f"{PB_URL}/api/collections/_superusers/auth-with-password", json={"identity": PB_EMAIL, "password": PB_PASSWORD})
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    url = f"{PB_URL}/api/collections/market_status/records?perPage=1&sort=-date"
    resp = requests.get(url, headers=headers)
    items = resp.json().get("items", [])
    if items:
        print(f"Latest record found: {items[0]['date']}")
        print(json.dumps(items[0]['data'], indent=2, ensure_ascii=False))
    else:
        print("Empty collection")

if __name__ == "__main__":
    check_latest()
