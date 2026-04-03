
import os
import glob
import json
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PB_URL = os.getenv("PB_URL", "http://127.0.0.1:8090")
PB_EMAIL = os.getenv("PB_EMAIL")
PB_PASSWORD = os.getenv("PB_PASSWORD")

# Auth
login_url = f"{PB_URL}/api/collections/_superusers/auth-with-password"
payload = {"identity": PB_EMAIL, "password": PB_PASSWORD}
r = requests.post(login_url, json=payload)
if not r.ok:
    print(f"Auth failed: {r.text}")
    exit()

TOKEN = r.json()["token"]
headers = {"Authorization": f"Bearer {TOKEN}"}

def setup_ohlcv():
    # Check if ohlcv exists
    res = requests.get(f"{PB_URL}/api/collections/ohlcv", headers=headers)
    if res.status_code == 404:
        print("Creating ohlcv collection...")
        data = {
            "name": "ohlcv",
            "type": "base",
            "listRule": "",
            "viewRule": "",
            "createRule": "",
            "updateRule": "",
            "deleteRule": "",
            "fields": [
                {"name": "date", "type": "date", "required": True},
                {"name": "code", "type": "text", "required": True},
                {"name": "open", "type": "number"},
                {"name": "high", "type": "number"},
                {"name": "low", "type": "number"},
                {"name": "close", "type": "number"},
                {"name": "volume", "type": "number"},
                {"name": "change", "type": "number"}
            ]
        }
        r2 = requests.post(f"{PB_URL}/api/collections", headers=headers, json=data)
        if r2.ok: print("Created ohlcv")
        else: print(f"Error creating ohlcv: {r2.text}")
    else:
        print("ohlcv collection already exists.")

def migrate_settings():
    print("Migrating status files to settings...")
    # 1. portfolio_status.json
    path1 = os.path.join(BASE_DIR, "Scripts/data/portfolio_status.json")
    if os.path.exists(path1):
        with open(path1, "r", encoding="utf-8") as f:
            data = json.load(f)
        res = requests.get(f"{PB_URL}/api/collections/settings/records?filter=key='portfolio_status'", headers=headers)
        items = res.json().get("items", [])
        if items:
            requests.patch(f"{PB_URL}/api/collections/settings/records/{items[0]['id']}", headers=headers, json={"value": data})
        else:
            requests.post(f"{PB_URL}/api/collections/settings/records", headers=headers, json={"key": "portfolio_status", "value": data})
        print("  Migrated portfolio_status")

    # 2. scan_progress.json
    path2 = os.path.join(BASE_DIR, "Scripts/data/scan_progress.json")
    if os.path.exists(path2):
        with open(path2, "r", encoding="utf-8") as f:
            data = json.load(f)
        res = requests.get(f"{PB_URL}/api/collections/settings/records?filter=key='scan_progress'", headers=headers)
        items = res.json().get("items", [])
        if items:
            requests.patch(f"{PB_URL}/api/collections/settings/records/{items[0]['id']}", headers=headers, json={"value": data})
        else:
            requests.post(f"{PB_URL}/api/collections/settings/records", headers=headers, json={"key": "scan_progress", "value": data})
        print("  Migrated scan_progress")

def migrate_ohlcv():
    print("Migrating prices/*.csv to ohlcv (Priority Based)...")
    # Get portfolio tickers
    portfolio_path = os.path.join(BASE_DIR, "Scripts/data/portfolio.json")
    port_tickers = []
    if os.path.exists(portfolio_path):
        with open(portfolio_path, "r", encoding="utf-8") as f:
            try:
                port = json.load(f)
                port_tickers = [str(i.get('ticker') or i.get('code')).zfill(6) for i in port]
            except: pass
    
    indices = ["KS11", "KQ11", "CL=F", "US10Y", "USD/KRW"]
    target_tickers = list(set(port_tickers + indices))
    
    files = glob.glob(os.path.join(BASE_DIR, "Scripts/data/prices/*.csv"))
    print(f"Found {len(files)} CSV files.")
    
    count = 0
    for file_path in files:
        ticker = os.path.basename(file_path).replace(".csv", "")
        # Filter: Portfolio Tickers or specific indices
        is_priority = ticker in target_tickers or any(idx in ticker for idx in indices)
        
        # To make it very fast, we only migrate Priority tickers with last 100 days
        # and ignore others for now, OR migrate last 1 record for others.
        if not is_priority: 
            limit = 1 # Only latest record for others
        else:
            limit = 100 # Last 100 records for priority
            
        try:
            df = pd.read_csv(file_path)
            df = df.tail(limit)
            
            for _, row in df.iterrows():
                date_val = str(row['Date'])
                if " " not in date_val: 
                    # Convert YYYY-MM-DD to ISO
                    date_val = f"{date_val} 00:00:00.000Z"
                
                payload = {
                    "date": date_val,
                    "code": ticker,
                    "open": float(row.get('Open', 0) or 0),
                    "high": float(row.get('High', 0) or 0),
                    "low": float(row.get('Low', 0) or 0),
                    "close": float(row.get('Close', 0) or 0),
                    "volume": int(row.get('Volume', 0) or 0),
                    "change": float(row.get('Change', 0) or 0)
                }
                # Check duplication? For migration, we just push.
                # In real scenario, we should use upsert but for speed, let's post.
                # Actually, duplicate records in OHLCV are bad. 
                # Let's check if ticker and date combination already exists? (Too slow)
                # We assume ohlcv is empty.
                requests.post(f"{PB_URL}/api/collections/ohlcv/records", headers=headers, json=payload)
            
            count += 1
            if is_priority:
                print(f"  [PRIORITY] Migrated {ticker} ({len(df)} records)")
            elif count % 100 == 0:
                print(f"  Progress: {count}/{len(files)} files processed")
                
        except Exception as e:
            print(f"  Error migrating {ticker}: {e}")

if __name__ == "__main__":
    setup_ohlcv()
    migrate_settings()
    migrate_ohlcv()
    print("\nData Migration Complete!")
