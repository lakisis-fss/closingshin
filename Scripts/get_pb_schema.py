import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

PB_URL = os.getenv("PB_URL", "http://localhost:8090")
PB_EMAIL = os.getenv("PB_EMAIL", "admin@example.com")
PB_PASSWORD = os.getenv("PB_PASSWORD", "admin1234")

def get_schema(collection_name):
    # Auth
    login_url = f"{PB_URL}/api/collections/_superusers/auth-with-password"
    r = requests.post(login_url, json={"identity": PB_EMAIL, "password": PB_PASSWORD})
    if not r.ok:
        print(f"Auth failed: {r.text}")
        return
    
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get Collection
    col_res = requests.get(f"{PB_URL}/api/collections/{collection_name}", headers=headers)
    if col_res.ok:
        col = col_res.json()
        print(f"--- Schema for {collection_name} ---")
        for field in col['fields']:
            print(f"  - {field['name']} ({field['type']})")
    else:
        print(f"Failed to get collection: {col_res.text}")

if __name__ == "__main__":
    import sys
    col_name = sys.argv[1] if len(sys.argv) > 1 else "news_analysis"
    get_schema(col_name)
