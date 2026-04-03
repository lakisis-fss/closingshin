import os
import requests
from dotenv import load_dotenv

load_dotenv()

PB_URL = os.getenv("PB_URL", "http://localhost:8090")
PB_EMAIL = os.getenv("PB_EMAIL", "admin@example.com")
PB_PASSWORD = os.getenv("PB_PASSWORD", "admin1234")

def list_collections():
    # 1. Auth (get token)
    auth_url = f"{PB_URL}/api/collections/_superusers/auth-with-password"
    res = requests.post(auth_url, json={"identity": PB_EMAIL, "password": PB_PASSWORD})
    if res.status_code != 200:
        print(f"Auth Error: {res.text}")
        return
    
    token = res.json()["token"]
    
    # 2. Get Collections
    coll_url = f"{PB_URL}/api/collections"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(coll_url, headers=headers)
    if res.status_code == 200:
        colls = res.json()["items"]
        print(f"--- TOTAL COLLECTIONS: {len(colls)} ---")
        for c in colls:
            print(f"- NAME: {c['name']} | ID: {c['id']}")
    else:
        print(f"Fetch Error: {res.text}")

if __name__ == "__main__":
    list_collections()
