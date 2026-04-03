import os
import requests
from dotenv import load_dotenv

load_dotenv()

PB_URL = os.getenv("PB_URL", "http://127.0.0.1:8090")
PB_EMAIL = os.getenv("PB_EMAIL")
PB_PASSWORD = os.getenv("PB_PASSWORD")

def setup_vcp_charts():
    print(f"Connecting to {PB_URL}...")
    
    # Auth
    login_url = f"{PB_URL}/api/collections/_superusers/auth-with-password"
    r = requests.post(login_url, json={"identity": PB_EMAIL, "password": PB_PASSWORD})
    if not r.ok:
        print("Auth failed.")
        return
    
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check if exists
    r = requests.get(f"{PB_URL}/api/collections/vcp_charts", headers=headers)
    if r.ok:
        print("Collection 'vcp_charts' already exists. Skipping creation.")
    else:
        # Create Collection
        print("Creating 'vcp_charts' collection...")
        data = {
            "name": "vcp_charts",
            "type": "base",
            "listRule": "",
            "viewRule": "",
            "createRule": "",
            "updateRule": "",
            "deleteRule": "",
            "fields": [
                {"name": "date", "type": "date", "required": True},
                {"name": "market", "type": "text", "required": True},
                {"name": "name", "type": "text", "required": True},
                {"name": "ticker", "type": "text", "required": True},
                {"name": "file", "type": "file", "options": {"maxSelect": 1, "maxSize": 5242880, "mimeTypes": ["image/png", "image/jpeg", "image/webp"]}}
            ],
            "indexes": [
                "CREATE INDEX idx_vcpc_date ON vcp_charts (date)",
                "CREATE INDEX idx_vcpc_ticker ON vcp_charts (ticker)",
                "CREATE UNIQUE INDEX idx_vcpc_composite ON vcp_charts (date, ticker)"
            ]
        }
        r = requests.post(f"{PB_URL}/api/collections", headers=headers, json=data)
        if r.ok:
            print("Successfully created 'vcp_charts' collection.")
        else:
            print(f"Failed to create collection: {r.text}")

if __name__ == "__main__":
    setup_vcp_charts()
