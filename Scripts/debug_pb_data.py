
import os
from pocketbase import PocketBase
from dotenv import load_dotenv

load_dotenv()

PB_URL = os.getenv("PB_URL")
PB_EMAIL = os.getenv("PB_EMAIL")
PB_PASSWORD = os.getenv("PB_PASSWORD")

pb = PocketBase(PB_URL)

try:
    # Admin auth
    admin_data = pb.admins.auth_with_password(PB_EMAIL, PB_PASSWORD)
    print("Auth Success")

    # Fetch market_status
    results = pb.collection("market_status").get_list(1, 1, {"sort": "-id"})
    if results.items:
        item = results.items[0]
        print(f"ID: {item.id}")
        print(f"Date: {item.date}")
        print(f"Data: {item.data}")
    else:
        print("No items found")

except Exception as e:
    print(f"Error: {e}")
