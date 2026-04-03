import os
from pocketbase import PocketBase
from dotenv import load_dotenv

load_dotenv()

PB_URL = os.getenv("PB_URL", "http://localhost:8090")
PB_EMAIL = os.getenv("PB_EMAIL", "admin@example.com")
PB_PASSWORD = os.getenv("PB_PASSWORD", "password123")

pb = PocketBase(PB_URL)

def test_auth():
    print(f"Testing PB Connection to {PB_URL}")
    print(f"Auth Email: {PB_EMAIL}")
    
    # 1. Try pb.admins (Older style)
    try:
        print("Attempting pb.admins.auth_with_password...")
        pb.admins.auth_with_password(PB_EMAIL, PB_PASSWORD)
        print("Success with pb.admins!")
        return
    except Exception as e:
        print(f"Failed with pb.admins: {e}")

    # 2. Try pb.collection('_superusers') (v0.23+ style)
    try:
        print("Attempting pb.collection('_superusers').auth_with_password...")
        pb.collection("_superusers").auth_with_password(PB_EMAIL, PB_PASSWORD)
        print("Success with _superusers!")
        return
    except Exception as e:
        print(f"Failed with _superusers: {e}")

if __name__ == "__main__":
    test_auth()
