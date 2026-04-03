import os
from pocketbase import PocketBase
from dotenv import load_dotenv

load_dotenv()

PB_URL = os.getenv("PB_URL", "http://localhost:8090")
PB_EMAIL = os.getenv("PB_EMAIL", "admin@example.com")
PB_PASSWORD = os.getenv("PB_PASSWORD", "password123")

pb = PocketBase(PB_URL)

def unlock_collections():
    try:
        # 로그인
        pb.admins.auth_with_password(PB_EMAIL, PB_PASSWORD)
        print(f"Connected to {PB_URL}")

        collections = [
            "vcp_reports", "news_analysis", "news", "stock_infos", 
            "portfolio", "market_status", "target_lists", "settings", "ohlcv"
        ]

        for coll_name in collections:
            try:
                # 컬렉션 가져오기
                coll = pb.collections.get_one(coll_name)
                # List/View Rule을 "" (공개)로 설정
                pb.collections.update(coll.id, {
                    "listRule": "",
                    "viewRule": "",
                    "createRule": "",
                    "updateRule": "",
                    "deleteRule": "" # 로컬 환경이므로 편의를 위해 전체 공개
                })
                print(f"Unlocked collection: {coll_name}")
            except Exception as e:
                print(f"Failed to unlock {coll_name}: {e}")

        print("\nAll collections are now public. Frontend should work.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    unlock_collections()
