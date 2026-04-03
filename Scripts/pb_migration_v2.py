
import os
import glob
import json
import pandas as pd
from pocketbase import PocketBase
from dotenv import load_dotenv

load_dotenv()

PB_URL = os.getenv("PB_URL")
PB_EMAIL = os.getenv("PB_EMAIL")
PB_PASSWORD = os.getenv("PB_PASSWORD")

pb = PocketBase(PB_URL)

def authenticate():
    try:
        pb.collection("_superusers").auth_with_password(PB_EMAIL, PB_PASSWORD)
        print(f"Connected to PocketBase at {PB_URL}")
    except Exception as e:
        print(f"Auth failed: {e}")
        exit(1)

def migrate_market_status():
    print("\n[Market Status Migration] Starting...")
    files = sorted(glob.glob("Scripts/data/market_status/status_*.json"))
    for file_path in files:
        # status_YYYYMMDD.json
        filename = os.path.basename(file_path)
        date_str = filename.replace("status_", "").split(".")[0]
        if not date_str.isdigit() or len(date_str) != 8:
            continue
            
        iso_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}T00:00:00Z"
        
        try:
            # Check exist
            pb.collection("market_status").get_first_list_item(f'date="{iso_date}"')
            print(f"  Skipping existing: {date_str}")
            continue
        except: pass

        with open(file_path, "r", encoding="utf-8") as f:
            status_data = json.load(f)
            
        try:
            pb.collection("market_status").create({
                "date": iso_date,
                "data": status_data
            })
            print(f"  Migrated Market Status: {date_str}")
        except Exception as e:
            print(f"  Error {date_str}: {e}")

def migrate_vcp_reports():
    print("\n[VCP Reports Migration] Starting...")
    files = sorted(glob.glob("Scripts/results/vcp_report_*.csv"))
    for file_path in files:
        filename = os.path.basename(file_path)
        date_str = filename.replace("vcp_report_", "").split(".")[0]
        iso_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}T00:00:00Z"
        
        try:
            df = pd.read_csv(file_path)
            # Take top 50
            df = df.head(50)
            
            for _, row in df.iterrows():
                ticker = str(row.get('ticker', '000000')).zfill(6)
                try:
                    pb.collection("vcp_reports").get_first_list_item(f'date="{iso_date}" && ticker="{ticker}"')
                    continue
                except: pass

                data = {
                    "date": iso_date,
                    "ticker": ticker,
                    "name": str(row.get('name', '')),
                    "market_name": str(row.get('market', '')),
                    "price": float(row.get('price', 0)),
                    "change_pct": float(row.get('change_pct', 0)),
                    "volume": int(row.get('volume', 0)),
                    "vcp_stage": int(row.get('vcp_stage', 0)),
                    "contractions_count": int(row.get('contractions_count', 0)),
                    "volume_dry_up": str(row.get('volume_dry_up')).lower() == 'true',
                    "relative_strength": float(row.get('relative_strength', 0)),
                    "pivot_point": float(row.get('pivot_point', 0)),
                    "pivot_distance_pct": float(row.get('pivot_distance_pct', 0)),
                    "is_target": str(row.get('is_target')).lower() == 'true'
                }
                
                # contractions_history as JSON
                history_str = str(row.get('contractions_history', '[]'))
                try:
                    data["contractions_history"] = json.loads(history_str.replace("'", '"'))
                except:
                    data["contractions_history"] = []

                pb.collection("vcp_reports").create(data)
            print(f"  Migrated VCP Report: {date_str}")
        except Exception as e:
            print(f"  Error VCP {date_str}: {e}")

if __name__ == "__main__":
    authenticate()
    migrate_market_status()
    migrate_vcp_reports()
    print("\nMigration v2 Complete!")
