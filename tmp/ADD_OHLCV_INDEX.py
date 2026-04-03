import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils
import requests
import json

def add_ohlcv_index():
    pb_url = os.getenv("PB_URL", "http://localhost:8090")
    token = pb_utils.get_pb_token()
    
    # 1. Get current collection data
    url = f"{pb_url}/api/collections/ohlcv"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        resp = requests.get(url, headers=headers)
        data = resp.json()
        
        # 2. Add index if not exists
        idx_str = "CREATE INDEX `idx_ohlcv_code_date` ON `ohlcv` (`code`, `date`)"
        if idx_str not in data.get('indexes', []):
            print(f"Adding index to {data['name']}...")
            data['indexes'].append(idx_str)
            
            # 3. Update collection
            update_url = f"{pb_url}/api/collections/{data['id']}"
            resp_update = requests.patch(update_url, headers=headers, json={"indexes": data['indexes']})
            if resp_update.status_code == 200:
                print("Successfully added index!")
            else:
                print(f"Failed to add index: {resp_update.text}")
        else:
            print("Index already exists.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_ohlcv_index()
