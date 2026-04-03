import sys
import os
import json
from datetime import datetime

# Add Scripts directory to path
sys.path.append(os.path.abspath('Scripts'))
import pb_utils

def migrate():
    portfolio_path = 'Scripts/data/portfolio.json'
    if not os.path.exists(portfolio_path):
        print(f"Error: {portfolio_path} not found.")
        return

    # Attempt different encodings for Korean files
    try:
        # Try UTF-8 with BOM (common for Windows-saved CSV/JSON)
        with open(portfolio_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except:
        # Fallback to CP949 if it fails
        try:
            with open(portfolio_path, 'r', encoding='cp949') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Final Error: Could not load JSON with any encoding: {e}")
            return
    
    print(f"Found {len(data)} items in portfolio.json. Starting migration...")
    
    success_count = 0
    for idx, item in enumerate(data):
        ticker = item.get('ticker')
        buy_date = item.get('buyDate')
        
        if not ticker or not buy_date:
            print(f"Skipping item {idx}: Missing ticker or buyDate.")
            continue
            
        # Clean item for PB (remove unwanted keys if any)
        clean_item = item.copy()
        
        # IMPORTANT: Remove local ID to let PB generate its own valid ID
        if 'id' in clean_item:
            clean_item.pop('id')

        # Trim ALL string fields for PB constraints (Strict 100-char just to be safe)
        for key, val in clean_item.items():
            if isinstance(val, str):
                clean_item[key] = val[:100]
            elif isinstance(val, dict) or isinstance(val, list):
                # Nested objects - PB expects JSON or string. 
                # If these are large, it might still fail if field is Text.
                pass

        try:
            # PB upsert - Define filter inside try
            filter_str = f'ticker="{ticker}" && buyDate="{buy_date}"'
            res = pb_utils.upsert_to_pb('portfolio', clean_item, filter_str)
            
            if res:
                success_count += 1
            else:
                # If None, it means it failed inside pb_utils (handled error)
                print(f"FAILED (Return None) item {idx} ({ticker}):")
                for k, v in clean_item.items():
                    print(f"  - {k}: length {len(str(v))}")
                # We can't see 'e' here easily since it was caught in pb_utils
                
        except Exception as e:
            print(f"EXCEPTION item {idx} ({ticker}): {e}")
            
    print(f"Migration finished. Success: {success_count} / {len(data)}")

    # 2. Portfolio Status Migration
    status_path = 'Scripts/data/portfolio_status.json'
    if os.path.exists(status_path):
        try:
            with open(status_path, 'r', encoding='cp949') as f:
                status_data = json.load(f)
        except:
            with open(status_path, 'r', encoding='utf-8-sig') as f:
                status_data = json.load(f)
        
        try:
            pb_utils.upsert_to_pb('settings', {"key": "portfolio_status", "value": status_data}, 'key="portfolio_status"')
            print("[MIGRATE] Portfolio status summary updated in 'settings'.")
        except Exception as e:
            print(f"[MIGRATE] Error saving status summary: {e}")

if __name__ == "__main__":
    migrate()
