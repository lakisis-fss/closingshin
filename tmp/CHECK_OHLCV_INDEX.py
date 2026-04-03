import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils
import requests
import json

def check_ohlcv_schema():
    pb_url = os.getenv("PB_URL", "http://localhost:8090")
    token = pb_utils.get_pb_token()
    
    # PocketBase Admin API for collections
    url = f"{pb_url}/api/collections/ohlcv"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        resp = requests.get(url, headers=headers)
        data = resp.json()
        print(f"Collection: {data['name']}")
        print(f"Schema: {json.dumps(data['schema'], indent=2)}")
        print(f"Indexes: {json.dumps(data.get('indexes', []), indent=2)}")
    except Exception as e:
        print(f"Error fetching schema: {e}")

if __name__ == "__main__":
    check_ohlcv_schema()
