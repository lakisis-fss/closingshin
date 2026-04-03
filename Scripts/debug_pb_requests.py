
import os
import requests
from dotenv import load_dotenv

load_dotenv()

PB_URL = os.getenv("PB_URL")
PB_EMAIL = os.getenv("PB_EMAIL")
PB_PASSWORD = os.getenv("PB_PASSWORD")

# Try to fetch as Public first
url = f"{PB_URL}/api/collections/market_status/records?limit=1&sort=-id"

try:
    print(f"Fetching from: {url}")
    r = requests.get(url)
    if r.ok:
        data = r.json()
        if data["items"]:
            item = data["items"][0]
            print(f"ID: {item.get('id')}")
            print(f"Date: {item.get('date')}")
            print(f"Data value: {item.get('data')}")
            print(f"Type of Data: {type(item.get('data'))}")
        else:
            print("No items found")
    else:
        print(f"Fetch failed: {r.status_code} {r.text}")

except Exception as e:
    print(f"Error: {e}")
