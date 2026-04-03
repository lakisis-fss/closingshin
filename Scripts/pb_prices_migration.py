import os
import glob
import pandas as pd
import requests
import json
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()

PB_URL = "http://localhost:8090"
PB_EMAIL = "admin@example.com"
PB_PASSWORD = "admin1234"
MAX_WORKERS = 10 # Slightly reduced to avoid overloading SQLite with many parallel writes

def get_token():
    url = f"{PB_URL}/api/collections/_superusers/auth-with-password"
    try:
        resp = requests.post(url, json={"identity": PB_EMAIL, "password": PB_PASSWORD})
        return resp.json().get("token")
    except Exception as e:
        print(f"Auth failed: {e}")
        return None

def ensure_ohlcv_collection(token):
    headers = {"Authorization": f"Bearer {token}"}
    check_url = f"{PB_URL}/api/collections/ohlcv"
    
    # Check if exists
    resp = requests.get(check_url, headers=headers)
    if resp.status_code == 200:
        print("Collection 'ohlcv' already exists.")
        return

    print("Creating 'ohlcv' collection (minimal)...")
    create_url = f"{PB_URL}/api/collections"
    schema = {
        "name": "ohlcv",
        "type": "base",
        "schema": [
            {"name": "code", "type": "text", "required": True},
            {"name": "date", "type": "date", "required": True},
            {"name": "open", "type": "number"},
            {"name": "high", "type": "number"},
            {"name": "low", "type": "number"},
            {"name": "close", "type": "number"},
            {"name": "volume", "type": "number"},
            {"name": "change", "type": "number"},
            {"name": "uid", "type": "text", "required": True}
        ]
        # Indexes removed for now to ensure compatibility
    }
    r = requests.post(create_url, headers=headers, json=schema)
    if r.status_code != 200:
        print(f"Failed to create collection: {r.text}")
    else:
        print("Collection 'ohlcv' created successfully.")

def upload_file(file_path, token):
    ticker = os.path.basename(file_path).replace(".csv", "")
    headers = {"Authorization": f"Bearer {token}"}
    upload_url = f"{PB_URL}/api/collections/ohlcv/records"
    
    try:
        df = pd.read_csv(file_path)
        count = 0
        skipped = 0
        for _, row in df.iterrows():
            date_val = str(row['Date'])
            if ' ' in date_val: date_val = date_val.split(' ')[0]
            uid = f"{ticker}_{date_val.replace('-', '')}"
            
            data = {
                "code": ticker,
                "date": f"{date_val} 00:00:00",
                "open": float(row['Open']) if not pd.isna(row['Open']) else 0,
                "high": float(row['High']) if not pd.isna(row['High']) else 0,
                "low": float(row['Low']) if not pd.isna(row['Low']) else 0,
                "close": float(row['Close']) if not pd.isna(row['Close']) else 0,
                "volume": int(row['Volume']) if not pd.isna(row['Volume']) else 0,
                "change": float(row['Change']) if not pd.isna(row['Change']) else 0,
                "uid": uid
            }
            
            resp = requests.post(upload_url, headers=headers, json=data)
            if resp.status_code in [200, 204]:
                count += 1
            else:
                # If UID already exists, it will fail with 400. That's fine (skipping).
                skipped += 1
        return f"Done: {ticker} (+{count})"
    except Exception as e:
        return f"Error: {ticker} - {e}"

if __name__ == "__main__":
    token = get_token()
    if not token:
        exit(1)

    ensure_ohlcv_collection(token)
    
    files = sorted(glob.glob("Scripts/data/prices/*.csv"), reverse=True)
    print(f"Starting migration of {len(files)} files...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # We output results one by one as they finish
        for result in executor.map(lambda f: upload_file(f, token), files):
            print(result)

    print("\nPrice Data Migration Complete!")
