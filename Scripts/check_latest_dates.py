import requests
import os
from dotenv import load_dotenv

load_dotenv()

PB_URL = os.getenv("PB_URL", "http://127.0.0.1:8090")
PB_EMAIL = os.getenv("PB_EMAIL")
PB_PASSWORD = os.getenv("PB_PASSWORD")

def check_latest_dates():
    login_url = f"{PB_URL}/api/collections/_superusers/auth-with-password"
    r = requests.post(login_url, json={"identity": PB_EMAIL, "password": PB_PASSWORD})
    if not r.ok:
        print("Auth failed")
        return
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    collections = ["market_status", "vcp_reports", "news_reports", "stock_infos"]
    for col in collections:
        url = f"{PB_URL}/api/collections/{col}/records?perPage=1&sort=-date"
        resp = requests.get(url, headers=headers)
        items = resp.json().get("items", [])
        if items:
            print(f"Latest {col}: {items[0]['date']} (ID: {items[0]['id']})")
        else:
            print(f"Latest {col}: EMPTY")

if __name__ == "__main__":
    check_latest_dates()
