
import os
import glob
import json
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PB_URL = os.getenv("PB_URL", "http://127.0.0.1:8090")
PB_EMAIL = os.getenv("PB_EMAIL")
PB_PASSWORD = os.getenv("PB_PASSWORD")

login_url = f"{PB_URL}/api/collections/_superusers/auth-with-password"
payload = {"identity": PB_EMAIL, "password": PB_PASSWORD}
r = requests.post(login_url, json=payload)
if not r.ok:
    print(f"Auth failed: {r.text}")
    exit()

TOKEN = r.json()["token"]
headers = {"Authorization": f"Bearer {TOKEN}"}

# Delete & Recreate Collections ensuring fields and public access
def setup_collections():
    cols = requests.get(f"{PB_URL}/api/collections?perPage=500", headers=headers).json().get("items", [])
    col_names = {c["name"]: c["id"] for c in cols}

    for name in ["market_status", "vcp_reports"]:
        if name in col_names:
            requests.delete(f"{PB_URL}/api/collections/{col_names[name]}", headers=headers)
            print(f"Deleted {name}")

    # Create market_status
    ms_data = {
        "name": "market_status",
        "type": "base",
        "listRule": "",
        "viewRule": "",
        "createRule": "",
        "updateRule": "",
        "deleteRule": "",
        "fields": [
            {"name": "date", "type": "date", "required": True},
            {"name": "data", "type": "json"}
        ]
    }
    r = requests.post(f"{PB_URL}/api/collections", headers=headers, json=ms_data)
    if r.ok:
        print("Created market_status")
    else:
        print(f"Error market_status: {r.text}")

    # Create vcp_reports
    vcp_data = {
        "name": "vcp_reports",
        "type": "base",
        "listRule": "",
        "viewRule": "",
        "createRule": "",
        "updateRule": "",
        "deleteRule": "",
        "fields": [
            {"name": "date", "type": "date", "required": True},
            {"name": "ticker", "type": "text", "required": True},
            {"name": "name", "type": "text"},
            {"name": "market_name", "type": "text"},
            {"name": "price", "type": "number"},
            {"name": "change_pct", "type": "number"},
            {"name": "volume", "type": "number"},
            {"name": "vcp_stage", "type": "number"},
            {"name": "contractions_count", "type": "number"},
            {"name": "contractions_history", "type": "json"},
            {"name": "volume_dry_up", "type": "bool"},
            {"name": "relative_strength", "type": "number"},
            {"name": "consolidation_weeks", "type": "number"},
            {"name": "pivot_point", "type": "number"},
            {"name": "pivot_distance_pct", "type": "number"},
            {"name": "is_target", "type": "bool"}
        ]
    }
    r = requests.post(f"{PB_URL}/api/collections", headers=headers, json=vcp_data)
    if r.ok:
        print("Created vcp_reports")
    else:
        print(f"Error vcp_reports: {r.text}")


def migrate_market_status():
    print("Migrating market_status...")
    files = sorted(glob.glob(os.path.join(BASE_DIR, "Scripts/data/market_status/status_*.json")))
    for file_path in files:
        date_str = os.path.basename(file_path).replace("status_", "").split(".")[0]
        if not date_str.isdigit() or len(date_str) != 8:
            continue
        iso_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} 00:00:00.000Z"
        
        with open(file_path, "r", encoding="utf-8") as f:
            status_data = json.load(f)
            
        r = requests.post(f"{PB_URL}/api/collections/market_status/records", headers=headers, json={
            "date": iso_date,
            "data": status_data
        })
        if r.ok:
            print(f"  Inserted MS: {date_str}")
        else:
            print(f"  Failed MS {date_str}: {r.text}")

def migrate_vcp_reports():
    print("Migrating vcp_reports...")
    files = sorted(glob.glob(os.path.join(BASE_DIR, "Scripts/results/vcp_report_*.csv")))
    for file_path in files:
        date_str = os.path.basename(file_path).replace("vcp_report_", "").split(".")[0]
        iso_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} 00:00:00.000Z"
        
        try:
            df = pd.read_csv(file_path).head(50)
            for _, row in df.iterrows():
                history_str = str(row.get('contractions_history', '[]')).replace("'", '"')
                try:
                    history = json.loads(history_str)
                except:
                    history = []
                
                payload = {
                    "date": iso_date,
                    "ticker": str(row.get('ticker', '0')).zfill(6),
                    "name": str(row.get('name', '')),
                    "market_name": str(row.get('market', '')),
                    "price": float(row.get('price', 0) or 0),
                    "change_pct": float(row.get('change_pct', 0) or 0),
                    "volume": int(row.get('volume', 0) or 0),
                    "vcp_stage": int(row.get('vcp_stage', 0) or 0),
                    "contractions_count": int(row.get('contractions_count', 0) or 0),
                    "contractions_history": history,
                    "volume_dry_up": str(row.get('volume_dry_up')).lower() == 'true',
                    "relative_strength": float(row.get('relative_strength', 0) or 0),
                    "consolidation_weeks": float(row.get('consolidation_weeks', 0) or 0),
                    "pivot_point": float(row.get('pivot_point', 0) or 0),
                    "pivot_distance_pct": float(row.get('pivot_distance_pct', 0) or 0),
                    "is_target": str(row.get('is_target')).lower() == 'true'
                }
                r = requests.post(f"{PB_URL}/api/collections/vcp_reports/records", headers=headers, json=payload)
                if not r.ok:
                    print(f"Failed VCP {ticker}: {r.text}")
            print(f"  Inserted VCP: {date_str}")
        except Exception as e:
            print(f"  Failed parsing {date_str}: {e}")

setup_collections()
migrate_market_status()
migrate_vcp_reports()
print("All Done!")
