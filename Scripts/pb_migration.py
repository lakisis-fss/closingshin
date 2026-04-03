import os
import glob
import json
import pandas as pd
import requests
from pocketbase import PocketBase
from pocketbase.utils import ClientResponseError
from dotenv import load_dotenv

load_dotenv()

PB_URL = "http://localhost:8090"
PB_EMAIL = "admin@example.com"
PB_PASSWORD = "admin1234"

pb = PocketBase(PB_URL)

def authenticate():
    try:
        auth_data = pb.collection("_superusers").auth_with_password(PB_EMAIL, PB_PASSWORD)
        print("Connected to PocketBase.")
        return auth_data.token
    except Exception as e:
        print(f"Auth failed: {e}")
        exit(1)

# --- 1차 마이그레이션 함수들 (Scripts/results 대상) ---

def migrate_vcp_reports():
    print("\n[VCP Reports Migration] Checking...")
    files = sorted(glob.glob("Scripts/results/vcp_report_*.csv"))

    for file_path in files:
        date_str = os.path.basename(file_path).split("_")[-1].split(".")[0]
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} 00:00:00"
        try:
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                ticker = str(row.get('ticker', '000000')).zfill(6)
                # 중복 체크
                try:
                    pb.collection("vcp_reports").get_first_list_item(f'date="{formatted_date}" && code="{ticker}"')
                    continue
                except: pass

                name = row.get('name', 'Unknown')
                market = row.get('market', 'KOSPI')
                chart_filename = f"{market}_{name}_{ticker}.png"
                chart_path = f"Scripts/results/charts/{date_str}/{chart_filename}"
                
                data = {
                    "date": formatted_date,
                    "code": ticker,
                    "name": name,
                    "score": float(row.get('vcp_score', 0)),
                    "pivot_price": float(row.get('pivot_point', 0)),
                }
                
                try:
                    files_payload = {}
                    if os.path.exists(chart_path):
                        files_payload = { "chart_image": (chart_filename, open(chart_path, "rb"), "image/png") }
                    
                    # SDK를 통해 데이터와 파일을 동시에 업로드
                    pb.collection("vcp_reports").create(data, files_payload)
                except Exception as e:
                    print(f"  Error {name}: {e}")
            print(f"  Processed Result: {date_str}")
        except Exception as e:
            print(f"  Failed File {date_str}: {e}")

def migrate_news_analysis():
    print("\n[News Analysis Migration] Checking...")
    files = sorted(glob.glob("Scripts/results/news_analysis_*.csv"))
    for file_path in files:
        date_str = os.path.basename(file_path).split("_")[-1].split(".")[0]
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} 00:00:00"
        try:
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                code = str(row.get('code', '000000')).zfill(6)
                title = row.get('title', 'No Title')
                try:
                    exists = pb.collection("news_analysis").get_first_list_item(f'date="{formatted_date}" && code="{code}" && title="{title}"')
                    continue
                except: pass
                data = {
                    "date": formatted_date,
                    "code": code,
                    "title": title,
                    "link": row.get('link', ''),
                    "sentiment_score": float(row.get('sentiment_score', 0)),
                    "summary": row.get('analysis', '')
                }
                pb.collection("news_analysis").create(data)
            print(f"  Processed News: {date_str}")
        except: pass

# --- 2차 마이그레이션 함수들 (Scripts/data 대상) ---

def migrate_portfolio_data():
    print("\n[Portfolio Data Migration] Starting...")
    portfolio_path = "Scripts/data/portfolio.json"
    if not os.path.exists(portfolio_path): return

    with open(portfolio_path, "r", encoding="utf-8") as f:
        portfolio = json.load(f)

    for item in portfolio:
        legacy_id = item.get("id")
        try:
            # 중복 체크
            pb.collection("portfolio").get_first_list_item(f'legacy_id="{legacy_id}"')
            continue
        except: pass

        data = {
            "code": item.get("ticker", "000000").zfill(6),
            "name": item.get("name", "Unknown"),
            "market": item.get("market", "KOSPI"),
            "buy_date": item.get("buyDate", ""),
            "buy_price": item.get("buyPrice", 0),
            "quantity": item.get("quantity", 0),
            "status": item.get("simulation", {}).get("status", "OPEN"),
            "memo": item.get("memo", ""),
            "exit_conditions": item.get("exitConditions", {}),
            "simulation_data": item.get("simulation", {}),
            "initial_scores": item.get("initialScores", {}),
            "legacy_id": legacy_id,
        }
        try:
            pb.collection("portfolio").create(data)
            print(f"  Migrated Portfolio Item: {data['name']}")
        except Exception as e:
            print(f"  Error Portfolio Item {data['name']}: {e}")

def migrate_market_status():
    print("\n[Market Status Migration] Starting...")
    files = sorted(glob.glob("Scripts/data/market_status/status_*.json"))
    for file_path in files:
        date_str = os.path.basename(file_path).replace("status_", "").split(".")[0]
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} 00:00:00"
        
        try:
            pb.collection("market_status").get_first_list_item(f'date="{formatted_date}"')
            continue
        except: pass

        with open(file_path, "r", encoding="utf-8") as f:
            status_data = json.load(f)
            
        try:
            pb.collection("market_status").create({
                "date": formatted_date,
                "data": status_data
            })
            print(f"  Processed Market Status: {date_str}")
        except: pass

def migrate_config_to_settings():
    print("\n[Settings Migration] Starting...")
    config_path = "Scripts/data/config.json"
    if not os.path.exists(config_path): return

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    for key, value in config.items():
        try:
            existing = pb.collection("settings").get_first_list_item(f'key="{key}"')
            continue
        except: pass
        
        try:
            pb.collection("settings").create({"key": key, "value": value})
            print(f"  Migrated Setting: {key}")
        except: pass

if __name__ == "__main__":
    authenticate()
    
    # 1차 작업 (Scripts/results)
    migrate_vcp_reports()
    migrate_news_analysis()
    
    # 2차 작업 (Scripts/data)
    migrate_portfolio_data()
    migrate_market_status()
    migrate_config_to_settings()
    
    print("\nMigration Complete!")
