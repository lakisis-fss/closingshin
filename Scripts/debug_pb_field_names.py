
import os
import requests
from dotenv import load_dotenv

load_dotenv()

PB_URL = os.getenv("PB_URL")
PB_EMAIL = os.getenv("PB_EMAIL")
PB_PASSWORD = os.getenv("PB_PASSWORD")

login_url = f"{PB_URL}/api/collections/_superusers/auth-with-password"
payload = {"identity": PB_EMAIL, "password": PB_PASSWORD}

try:
    r = requests.post(login_url, json=payload)
    if r.ok:
        token = r.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        info = requests.get(f"{PB_URL}/api/collections/market_status", headers=headers).json()
        print(f"Collection: {info['name']}")
        if 'fields' in info:
            print("Fields Names (v1.0):")
            for f in info['fields']:
                print(f"  - {f['name']} ({f['type']})")
        if 'schema' in info:
            print("Schema Names (old):")
            for f in info['schema']:
                print(f"  - {f['name']} ({f['type']})")

except Exception as e:
    print(f"Error: {e}")
