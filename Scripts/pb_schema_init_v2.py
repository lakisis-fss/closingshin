
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

def create_collection(name, fields, indexes=None):
    try:
        # Check if exists
        try:
            coll = pb.collections.get_one(name)
            print(f"Collection '{name}' exists. Deleting for clean restart...")
            pb.collections.delete(coll.id)
        except:
            pass
            
        # Create new
        data = {
            "name": name,
            "type": "base",
            "schema": fields,
            "listRule": "",
            "viewRule": "",
            "createRule": "",
            "updateRule": "",
            "deleteRule": "",
            "indexes": indexes or []
        }
        pb.collections.create(data)
        print(f"Created collection: {name}")
    except Exception as e:
        print(f"Error creating collection {name}: {e}")

def main():
    print("Initializing PocketBase Schema (Standard v1.0)...")

    # News Collection
    create_collection("news", [
        {"name": "ticker", "type": "text", "required": True},
        {"name": "name", "type": "text"},
        {"name": "title", "type": "text", "required": True},
        {"name": "pub_date", "type": "date"},
        {"name": "link", "type": "text"},
        {"name": "description", "type": "text"},
        {"name": "score", "type": "number"},
        {"name": "uid", "type": "text", "unique": True}
    ])

    # News Analysis
    create_collection("news_analysis", [
        {"name": "date", "type": "date", "required": True},
        {"name": "target_stock", "type": "text", "required": True},
        {"name": "analysis", "type": "text"},
        {"name": "sentiment_score", "type": "number"},
        {"name": "key_themes", "type": "json"}
    ])

    # Stock Infos
    create_collection("stock_infos", [
        {"name": "ticker", "type": "text", "required": True, "unique": True},
        {"name": "name", "type": "text"},
        {"name": "market", "type": "text"},
        {"name": "sector", "type": "text"},
        {"name": "industry", "type": "text"},
        {"name": "listing_date", "type": "date"},
        {"name": "summary", "type": "text"}
    ])

    # VCP Reports
    create_collection("vcp_reports", [
        {"name": "date", "type": "date", "required": True},
        {"name": "ticker", "type": "text", "required": True},
        {"name": "name", "type": "text"},
        {"name": "market_name", "type": "text"},
        {"name": "price", "type": "number"},
        {"name": "change_pct", "type": "number"},
        {"name": "volume", "type": "number"},
        {"name": "vcp_stage", "type": "number"},
        {"name": "contractions_count", "type": "number"},
        {"name": "contractions_history", "type": "json"},
        {"name": "volume_dry_up", "type": "bool"},
        {"name": "relative_strength", "type": "number"},
        {"name": "consolidation_weeks", "type": "number"},
        {"name": "pivot_point", "type": "number"},
        {"name": "pivot_distance_pct", "type": "number"},
        {"name": "is_target", "type": "bool"}
    ])

    # Portfolio
    create_collection("portfolio", [
        {"name": "code", "type": "text", "required": True},
        {"name": "name", "type": "text"},
        {"name": "entry_date", "type": "date", "required": True},
        {"name": "entry_price", "type": "number", "required": True},
        {"name": "quantity", "type": "number"},
        {"name": "status", "type": "text"},
        {"name": "memo", "type": "text"},
        {"name": "exit_conditions", "type": "json"},
        {"name": "simulation_data", "type": "json"}
    ])

    # Market Status
    create_collection("market_status", [
        {"name": "date", "type": "date", "required": True, "unique": True},
        {"name": "data", "type": "json"}
    ])

    print("Schema initialization complete!")

if __name__ == "__main__":
    main()
