import os
import requests
from dotenv import load_dotenv

load_dotenv()

PB_URL = os.getenv("PB_URL", "http://127.0.0.1:8090")
PB_EMAIL = os.getenv("PB_EMAIL")
PB_PASSWORD = os.getenv("PB_PASSWORD")

def check():
    print(f"Connecting to {PB_URL}...")
    
    # Auth
    login_url = f"{PB_URL}/api/collections/_superusers/auth-with-password"
    r = requests.post(login_url, json={"identity": PB_EMAIL, "password": PB_PASSWORD})
    if not r.ok:
        print("Auth failed.")
        return
    
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # List Collections
    r = requests.get(f"{PB_URL}/api/collections?perPage=500", headers=headers)
    if not r.ok:
        print("Failed to list collections.")
        return
    
    items = r.json().get("items", [])
    print(f"Found {len(items)} collections:")
    for item in items:
        name = item["name"]
        fields = item.get("fields", [])
        # Check if any field is of type 'file'
        has_file = any(f.get("type") == "file" for f in fields)
        print(f"- {name} (Has File Field: {has_file})")
        if has_file:
            file_fields = [f.get("name") for f in fields if f.get("type") == "file"]
            print(f"  -> File Fields: {file_fields}")

if __name__ == "__main__":
    check()
