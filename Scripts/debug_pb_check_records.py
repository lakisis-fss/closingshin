
import os
from pocketbase import PocketBase
from dotenv import load_dotenv

load_dotenv()

PB_URL = os.getenv("PB_URL")
PB_EMAIL = os.getenv("PB_EMAIL")
PB_PASSWORD = os.getenv("PB_PASSWORD")

pb = PocketBase(PB_URL)
# Login as superuser
pb.collection('_superusers').auth_with_password(PB_EMAIL, PB_PASSWORD)

print("Checking market_status collection...")
try:
    records = pb.collection("market_status").get_list(1, 10)
    print(f"Total items in market_status: {records.total_items}")
    if records.items:
        print(f"First item: {records.items[0].__dict__}")
except Exception as e:
    print(f"Error fetching: {e}")

print("Checking permissions...")
try:
    coll = pb.collections.get_one("market_status")
    print(f"List Rule: {getattr(coll, 'list_rule', getattr(coll, 'listRule', 'N/A'))}")
    print(f"View Rule: {getattr(coll, 'view_rule', getattr(coll, 'viewRule', 'N/A'))}")
except Exception as e:
    print(f"Error checking coll: {e}")
