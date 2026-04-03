from pocketbase import PocketBase
import os
from dotenv import load_dotenv

load_dotenv()
PB_URL = os.getenv("PB_URL", "http://localhost:8090")
PB_EMAIL = os.getenv("PB_EMAIL", "admin@example.com")
PB_PASSWORD = os.getenv("PB_PASSWORD", "admin1234")

pb = PocketBase(PB_URL)
pb.collection("_superusers").auth_with_password(PB_EMAIL, PB_PASSWORD)

def check():
    print("Checking vcp_reports...")
    try:
        recs = pb.collection("vcp_reports").get_list(1, 20)
        print(f"Total Items: {recs.total_items}")
        for r in recs.items:
            print(f"  ID: {r.id} | Date: {r.date} | Ticker: {r.ticker}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
