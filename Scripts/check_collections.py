from pocketbase import PocketBase
from dotenv import load_dotenv

load_dotenv()

PB_URL = "http://localhost:8090"
PB_EMAIL = "admin@example.com"
PB_PASSWORD = "admin1234"

pb = PocketBase(PB_URL)
pb.collection("_superusers").auth_with_password(PB_EMAIL, PB_PASSWORD)

collections = pb.collections.get_full_list()
for c in collections:
    print(f"- {c.name}")
