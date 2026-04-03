import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils
from collections import defaultdict

def cleanup_collection(collection_name, unique_fields):
    print(f"--- Cleaning up {collection_name} ---")
    # Fetch all records (batch if too many)
    recs = pb_utils.query_pb(collection_name, limit=5000)
    if not recs:
        print(f"No records found in {collection_name}")
        return

    seen = set()
    to_delete = []
    
    for r in recs:
        # Create a unique key based on specified fields and date (normalized to 10 chars)
        date_key = r['date'][:10]
        key_parts = [date_key]
        for f in unique_fields:
            key_parts.append(str(r.get(f, '')))
        
        unique_key = "|".join(key_parts)
        
        if unique_key in seen:
            to_delete.append(r['id'])
        else:
            seen.add(unique_key)
            
    print(f"Found {len(to_delete)} duplicates out of {len(recs)} total records.")
    
    for rid in to_delete:
        try:
            pb_utils.get_pb_client().collection(collection_name).delete(rid)
            print(f"  Deleted duplicate: {rid}")
        except Exception as e:
            print(f"  Failed to delete {rid}: {e}")

if __name__ == "__main__":
    # 1. vcp_reports (date + ticker)
    cleanup_collection("vcp_reports", ["ticker"])
    
    # 2. stock_infos (date + ticker)
    cleanup_collection("stock_infos", ["ticker"])
    
    # 3. news (date + link/title)
    cleanup_collection("news", ["link", "ticker"])
    
    # 4. news_analysis (date + link)
    cleanup_collection("news_analysis", ["link"])
    
    print("Cleanup complete.")
