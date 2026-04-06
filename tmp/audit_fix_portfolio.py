import requests
import json

pb_url = "http://127.0.0.1:8090"

def audit_and_fix():
    print("--- Collection Schema Audit ---")
    try:
        # 1. Get collection info
        res = requests.get(f"{pb_url}/api/collections/portfolio")
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
            print(f"Failed to fetch portfolio schema: {res.status_code}")
            
        # 2. Check Specific Records
        print("\n--- Checking Specific Records ---")
        items_res = requests.get(f"{pb_url}/api/collections/portfolio/records?limit=100")
        items = items_res.json().get('items', [])
        
        targets = ['052860', '065530']
        for item in items:
            ticker = item.get('ticker')
            if ticker in targets:
                print(f"Ticker: {ticker}, Name: {item.get('name')}, Current vcp_mode: '{item.get('vcp_mode')}'")
                
                # FIX: Update vcp_mode to 'classic' if it's empty
                if not item.get('vcp_mode'):
                    print(f"  -> Fixing vcp_mode for {item.get('name')}...")
                    patch_res = requests.patch(
                        f"{pb_url}/api/collections/portfolio/records/{item.get('id')}",
                        json={"vcp_mode": "classic"}
                    )
                    if patch_res.status_code == 200:
                        print(f"  -> SUCCESS: Updated to 'classic'")
                    else:
                        print(f"  -> FAILED: {patch_res.status_code} {patch_res.text}")

    except Exception as e:
        print(f"Error during audit: {e}")

if __name__ == "__main__":
    audit_and_fix()
