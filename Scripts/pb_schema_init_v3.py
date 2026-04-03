
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
            print(f"Collection '{name}' exists. Deleting for reconstruction...")
            pb.collections.delete(coll.id)
        except:
            pass
            
        # PocketBase v1.0 parameters: name, type, fields, indexes, listRule, etc.
        # But wait, pb.collections.create() usually expects a DICT
        data = {
            "name": name,
            "type": "base",
            "fields": fields, # Standard v1.0 naming
            "listRule": "",
            "viewRule": "",
            "createRule": "",
            "updateRule": "",
            "deleteRule": "",
            "indexes": indexes or []
        }
        
        # In v1.0, some fields are named differently. 
        # Actually, let's use the 'schema' key as fallback if it fails, or search the library.
        # Actually, let's try 'fields' first as it's the 1.0 standard.
        try:
             pb.collections.create(data)
             print(f"Created collection: {name}")
        except Exception as e:
             print(f"  Retrying with old 'schema' key for {name} due to: {e}")
             data["schema"] = fields
             del data["fields"]
             pb.collections.create(data)
             print(f"  Created collection {name} using old 'schema' key (Backward compatibility).")

    except Exception as e:
        print(f"CRITICAL Error creating collection {name}: {e}")

def main():
    print("PocketBase v1.0 Schema Reconstruction Starting...")

    # Market Status
    create_collection("market_status", [
        {"name": "date", "type": "date", "required": True},
        {"name": "data", "type": "json"}
    ], ["CREATE UNIQUE INDEX idx_ms_date ON market_status (date)"])

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
    ], ["CREATE INDEX idx_vcp_date ON vcp_reports (date)", "CREATE INDEX idx_vcp_ticker ON vcp_reports (ticker)"])

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

    print("\nSchema Reconstruction Complete!")

if __name__ == "__main__":
    main()
