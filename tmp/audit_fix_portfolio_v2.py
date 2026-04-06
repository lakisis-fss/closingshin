import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Scripts')))

import pb_utils
import requests
import json

def audit_and_fix():
    print("--- Collection Schema Audit (Auth) ---")
    try:
        # Get Admin Token
        token = pb_utils.get_pb_token()
        if not token:
            print("Failed to get PB token.")
            return

        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Get collection info
        res = requests.get(f"{pb_utils.PB_URL}/api/collections/portfolio", headers=headers)
        if res.status_code == 200:
            data = res.json()
            schema = data.get('schema', [])
            fields = [f['name'] for f in schema]
            print(f"Collection: portfolio")
            print(f"Fields found: {fields}")
            
            if 'vcp_mode' not in fields:
                print("WARNING: 'vcp_mode' field is MISSING in portfolio schema!")
            else:
                print("SUCCESS: 'vcp_mode' field is present in schema.")
        else:
            print(f"Failed to fetch portfolio schema: {res.status_code} {res.text}")
            
        # 2. Check Specific Records
        print("\n--- Checking Specific Records ---")
        # Use query_pb helper
        items = pb_utils.query_pb("portfolio", limit=200)
        
        targets = ['052860', '065530']
        for item in items:
            ticker = item.get('ticker')
            if ticker in targets:
                print(f"Ticker: {ticker}, Name: {item.get('name')}, Current vcp_mode: '{item.get('vcp_mode')}'")
                
                # FIX: Update vcp_mode to 'classic'
                print(f"  -> Fixing vcp_mode for {item.get('name')}...")
                success = pb_utils.upsert_to_pb(
                    "portfolio", 
                    {"vcp_mode": "classic"}, 
                    f'id="{item.get("id")}"',
                    token=token
                )
                if success:
                    print(f"  -> SUCCESS: Updated to 'classic'")
                else:
                    print(f"  -> FAILED to update")

    except Exception as e:
        print(f"Error during audit: {e}")

if __name__ == "__main__":
    audit_and_fix()
