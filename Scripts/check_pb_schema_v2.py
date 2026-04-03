import requests
import os
from dotenv import load_dotenv

load_dotenv()

PB_URL = os.getenv("PB_URL", "http://localhost:8090")
PB_EMAIL = os.getenv("PB_EMAIL", "admin@example.com")
PB_PASSWORD = os.getenv("PB_PASSWORD", "admin1234")

def check_schema():
    login_url = f"{PB_URL}/api/collections/_superusers/auth-with-password"
    r = requests.post(login_url, json={"identity": PB_EMAIL, "password": PB_PASSWORD})
    if not r.ok:
        print(f"Auth failed: {r.text}")
        return
    
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    col_res = requests.get(f"{PB_URL}/api/collections/stock_infos", headers=headers)
    if col_res.ok:
        col = col_res.json()
        print(f"Collection: {col['name']}")
        for field in col['fields']:
            print(f"  - {field['name']} ({field['type']})")
    else:
        print(f"Failed to get collection: {col_res.text}")

    print("\n--- Sample Record (March 16) ---")
    filter_str = 'date >= "2026-03-16 00:00:00.000Z" && date < "2026-03-17 00:00:00.000Z"'
    rec_res = requests.get(f"{PB_URL}/api/collections/stock_infos/records?filter={filter_str}&perPage=1", headers=headers)
    if rec_res.ok:
        items = rec_res.json().get("items", [])
        if items:
            print(json.dumps(items[0], indent=2, ensure_ascii=False))
        else:
            print("No records found for March 16")
    else:
        print(f"Failed to get records: {rec_res.text}")

if __name__ == "__main__":
    import json
    check_schema()
