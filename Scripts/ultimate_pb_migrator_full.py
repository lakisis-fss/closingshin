
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

def setup_collections():
    cols = requests.get(f"{PB_URL}/api/collections?perPage=500", headers=headers).json().get("items", [])
    col_names = {c["name"]: c["id"] for c in cols}

    # All collections to migrate
    collections_to_setup = [
        {
            "name": "market_status",
            "fields": [
                {"name": "date", "type": "date", "required": True},
                {"name": "data", "type": "json"}
            ]
        },
        {
            "name": "vcp_reports",
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
        },
        {
            "name": "news_reports",
            "fields": [
                {"name": "date", "type": "date", "required": True},
                {"name": "ticker", "type": "text", "required": True},
                {"name": "name", "type": "text"},
                {"name": "title", "type": "text"},
                {"name": "pub_date", "type": "date"},
                {"name": "link", "type": "text"},
                {"name": "description", "type": "text"},
                {"name": "score", "type": "number"}
            ]
        },
        {
            "name": "news_analysis",
            "fields": [
                {"name": "date", "type": "date", "required": True},
                {"name": "ticker", "type": "text", "required": True},
                {"name": "name", "type": "text"},
                {"name": "title", "type": "text"},
                {"name": "pub_date", "type": "date"},
                {"name": "link", "type": "text"},
                {"name": "description", "type": "text"},
                {"name": "score", "type": "number"},
                {"name": "target_stock", "type": "text"},
                {"name": "sentiment_score", "type": "number"},
                {"name": "sentiment_label", "type": "text"},
                {"name": "impact_intensity", "type": "text"},
                {"name": "time_horizon", "type": "text"},
                {"name": "news_type", "type": "text"},
                {"name": "key_drivers", "type": "text"},
                {"name": "trading_signal", "type": "text"},
                {"name": "reason", "type": "text"}
            ]
        },
        {
            "name": "stock_infos",
            "fields": [
                {"name": "date", "type": "date", "required": True},
                {"name": "ticker", "type": "text", "required": True},
                {"name": "name", "type": "text"},
                {"name": "collection_date", "type": "date"},
                {"name": "PER", "type": "number"},
                {"name": "PBR", "type": "number"},
                {"name": "EPS", "type": "number"},
                {"name": "BPS", "type": "number"},
                {"name": "DIV", "type": "number"},
                {"name": "DPS", "type": "number"},
                {"name": "기관_5일", "type": "number"},
                {"name": "외인_5일", "type": "number"},
                {"name": "개인_5일", "type": "number"},
                {"name": "기관_15일", "type": "number"},
                {"name": "외인_15일", "type": "number"},
                {"name": "개인_15일", "type": "number"},
                {"name": "기관_30일", "type": "number"},
                {"name": "외인_30일", "type": "number"},
                {"name": "개인_30일", "type": "number"},
                {"name": "기관_50일", "type": "number"},
                {"name": "외인_50일", "type": "number"},
                {"name": "개인_50일", "type": "number"},
                {"name": "기관_100일", "type": "number"},
                {"name": "외인_100일", "type": "number"},
                {"name": "개인_100일", "type": "number"},
                {"name": "supply_score", "type": "number"},
                {"name": "fundamental_score", "type": "number"},
                {"name": "market_cap", "type": "number"},
                {"name": "price_change_pct", "type": "number"},
                {"name": "close", "type": "number"}
            ]
        },
        {
            "name": "portfolio",
            "fields": [
                {"name": "legacy_id", "type": "text"},
                {"name": "ticker", "type": "text", "required": True},
                {"name": "name", "type": "text"},
                {"name": "market", "type": "text"},
                {"name": "buyDate", "type": "date"},
                {"name": "buyPrice", "type": "number"},
                {"name": "quantity", "type": "number"},
                {"name": "memo", "type": "text"},
                {"name": "exitPlan", "type": "text"},
                {"name": "exitConditions", "type": "json"},
                {"name": "vcp_mode", "type": "text"},
                {"name": "initialScores", "type": "json"},
                {"name": "simulation", "type": "json"}
            ]
        },
        {
            "name": "settings",
            "fields": [
                {"name": "key", "type": "text", "required": True},
                {"name": "value", "type": "json"}
            ]
        }
    ]

    for col in collections_to_setup:
        name = col["name"]
        if name in col_names:
            requests.delete(f"{PB_URL}/api/collections/{col_names[name]}", headers=headers)
            print(f"Deleted {name}")

        data = {
            "name": name,
            "type": "base",
            "listRule": "",
            "viewRule": "",
            "createRule": "",
            "updateRule": "",
            "deleteRule": "",
            "fields": col["fields"]
        }
        r = requests.post(f"{PB_URL}/api/collections", headers=headers, json=data)
        if r.ok:
            print(f"Created {name}")
        else:
            print(f"Error {name}: {r.text}")

def migrate_market_status():
    print("Migrating market_status...")
    files = sorted(glob.glob(os.path.join(BASE_DIR, "Scripts/data/market_status/status_*.json")))
    for file_path in files:
        date_str = os.path.basename(file_path).replace("status_", "").split(".")[0]
        if not date_str.isdigit() or len(date_str) != 8: continue
        iso_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} 00:00:00.000Z"
        with open(file_path, "r", encoding="utf-8") as f:
            status_data = json.load(f)
        requests.post(f"{PB_URL}/api/collections/market_status/records", headers=headers, json={"date": iso_date, "data": status_data})
    print("  Done market_status")

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
                try: history = json.loads(history_str)
                except: history = []
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
                    "volume_dry_up": str(row.get('volume_dry_up')).lower() in ['true', '1'],
                    "relative_strength": float(row.get('relative_strength', 0) or 0),
                    "consolidation_weeks": float(row.get('consolidation_weeks', 0) or 0),
                    "pivot_point": float(row.get('pivot_point', 0) or 0),
                    "pivot_distance_pct": float(row.get('pivot_distance_pct', 0) or 0),
                    "is_target": str(row.get('is_target')).lower() in ['true', '1']
                }
                requests.post(f"{PB_URL}/api/collections/vcp_reports/records", headers=headers, json=payload)
            print(f"  Inserted VCP: {date_str}")
        except Exception as e: print(f"  Failed VCP {date_str}: {e}")

def migrate_news_reports():
    print("Migrating news_reports...")
    files = sorted(glob.glob(os.path.join(BASE_DIR, "Scripts/results/news_report_*.csv")))
    for file_path in files:
        date_str = os.path.basename(file_path).replace("news_report_", "").split(".")[0]
        iso_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} 00:00:00.000Z"
        try:
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                payload = {
                    "date": iso_date,
                    "ticker": str(row.get('ticker', '0')).zfill(6),
                    "name": str(row.get('name', '')),
                    "title": str(row.get('title', '')),
                    "pub_date": str(row.get('pub_date', '')),
                    "link": str(row.get('link', '')),
                    "description": str(row.get('description', '')),
                    "score": float(row.get('score', 0) or 0)
                }
                requests.post(f"{PB_URL}/api/collections/news_reports/records", headers=headers, json=payload)
            print(f"  Inserted News Report: {date_str}")
        except Exception as e: print(f"  Failed News Report {date_str}: {e}")

def migrate_news_analysis():
    print("Migrating news_analysis...")
    files = sorted(glob.glob(os.path.join(BASE_DIR, "Scripts/results/news_analysis_*.csv")))
    for file_path in files:
        date_str = os.path.basename(file_path).replace("news_analysis_", "").split(".")[0]
        iso_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} 00:00:00.000Z"
        try:
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                payload = {
                    "date": iso_date,
                    "ticker": str(row.get('ticker', '0')).zfill(6),
                    "name": str(row.get('name', '')),
                    "title": str(row.get('title', '')),
                    "pub_date": str(row.get('pub_date', '')),
                    "link": str(row.get('link', '')),
                    "description": str(row.get('description', '')),
                    "score": float(row.get('score', 0) or 0),
                    "target_stock": str(row.get('target_stock', '')),
                    "sentiment_score": float(row.get('sentiment_score', 0) or 0),
                    "sentiment_label": str(row.get('sentiment_label', '')),
                    "impact_intensity": str(row.get('impact_intensity', '')),
                    "time_horizon": str(row.get('time_horizon', '')),
                    "news_type": str(row.get('news_type', '')),
                    "key_drivers": str(row.get('key_drivers', '')),
                    "trading_signal": str(row.get('trading_signal', '')),
                    "reason": str(row.get('reason', ''))
                }
                requests.post(f"{PB_URL}/api/collections/news_analysis/records", headers=headers, json=payload)
            print(f"  Inserted News Analysis: {date_str}")
        except Exception as e: print(f"  Failed News Analysis {date_str}: {e}")

def migrate_stock_infos():
    print("Migrating stock_infos...")
    files = sorted(glob.glob(os.path.join(BASE_DIR, "Scripts/results/stock_info_*.csv")))
    for file_path in files:
        date_str = os.path.basename(file_path).replace("stock_info_", "").split(".")[0]
        iso_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} 00:00:00.000Z"
        try:
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                payload = {
                    "date": iso_date,
                    "ticker": str(row.get('ticker', '0')).zfill(6),
                    "name": str(row.get('name', '')),
                    "collection_date": str(row.get('collection_date', '')),
                    "PER": float(row.get('PER', 0) or 0),
                    "PBR": float(row.get('PBR', 0) or 0),
                    "EPS": float(row.get('EPS', 0) or 0),
                    "BPS": float(row.get('BPS', 0) or 0),
                    "DIV": float(row.get('DIV', 0) or 0),
                    "DPS": float(row.get('DPS', 0) or 0),
                    "기관_5일": float(row.get('기관_5일', 0) or 0),
                    "외인_5일": float(row.get('외인_5일', 0) or 0),
                    "개인_5일": float(row.get('개인_5일', 0) or 0),
                    "기관_15일": float(row.get('기관_15일', 0) or 0),
                    "외인_15일": float(row.get('외인_15일', 0) or 0),
                    "개인_15일": float(row.get('개인_15일', 0) or 0),
                    "기관_30일": float(row.get('기관_30일', 0) or 0),
                    "외인_30일": float(row.get('외인_30일', 0) or 0),
                    "개인_30일": float(row.get('개인_30일', 0) or 0),
                    "기관_50일": float(row.get('기관_50일', 0) or 0),
                    "외인_50일": float(row.get('외인_50일', 0) or 0),
                    "개인_50일": float(row.get('개인_50일', 0) or 0),
                    "기관_100일": float(row.get('기관_100일', 0) or 0),
                    "외인_100일": float(row.get('외인_100일', 0) or 0),
                    "개인_100일": float(row.get('개인_100일', 0) or 0),
                    "supply_score": float(row.get('supply_score', 0) or 0),
                    "fundamental_score": float(row.get('fundamental_score', 0) or 0),
                    "market_cap": float(row.get('market_cap', 0) or 0),
                    "price_change_pct": float(row.get('price_change_pct', 0) or 0),
                    "close": float(row.get('close', 0) or 0)
                }
                requests.post(f"{PB_URL}/api/collections/stock_infos/records", headers=headers, json=payload)
            print(f"  Inserted Stock Info: {date_str}")
        except Exception as e: print(f"  Failed Stock Info {date_str}: {e}")

def migrate_portfolio():
    print("Migrating portfolio...")
    file_path = os.path.join(BASE_DIR, "Scripts/data/portfolio.json")
    if not os.path.exists(file_path): return
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        payload = {
            "legacy_id": str(item.get("id", "")),
            "ticker": str(item.get("ticker", "0")).zfill(6),
            "name": str(item.get("name", "")),
            "market": str(item.get("market", "")),
            "buyDate": str(item.get("buyDate", "")),
            "buyPrice": float(item.get("buyPrice", 0) or 0),
            "quantity": int(item.get("quantity", 0) or 0),
            "memo": str(item.get("memo", "")),
            "exitPlan": str(item.get("exitPlan", "")),
            "exitConditions": item.get("exitConditions", {}),
            "vcp_mode": str(item.get("vcp_mode", "")),
            "initialScores": item.get("initialScores", {}),
            "simulation": item.get("simulation", {})
        }
        requests.post(f"{PB_URL}/api/collections/portfolio/records", headers=headers, json=payload)
    print("  Done portfolio")

def migrate_settings():
    print("Migrating settings...")
    file_path = os.path.join(BASE_DIR, "Scripts/data/config.json")
    if not os.path.exists(file_path): return
    with open(file_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    for key, value in config.items():
        requests.post(f"{PB_URL}/api/collections/settings/records", headers=headers, json={"key": key, "value": value})
    print("  Done settings")

if __name__ == "__main__":
    setup_collections()
    migrate_market_status()
    migrate_vcp_reports()
    migrate_news_reports()
    migrate_news_analysis()
    migrate_stock_infos()
    migrate_portfolio()
    # migrate_settings() # Optional, depending on if you want to move config
    print("\nMigration Full Complete!")
