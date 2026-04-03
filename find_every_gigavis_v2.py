import os
import sys
import json

# Add the Scripts directory to the path so we can import pb_utils
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))

import pb_utils

def find_every_gigavis_v2():
    print("Searching for ALL records that might be 'Gigavis' (기가비스) in ALL related collections...")
    
    collections = ["portfolio", "stock_infos", "vcp_reports"]
    
    results = {}
    for coll in collections:
        print(f"Checking collection: {coll}")
        try:
            recs = pb_utils.query_pb(coll, filter_str='name~"기가비스" || ticker~"420770"')
            results[coll] = recs
        except:
            print(f"Failed to query {coll}")
            
    print("\n--- Summary ---")
    for coll, recs in results.items():
        print(f"Collection {coll}: {len(recs)} records found.")
        for r in recs:
            print(f"  [ID: {r.get('id')}] Ticker: {r.get('ticker')}, Name: {r.get('name')}")
            # Identify simulation fields
            for k in r.keys():
                if 'sim' in k.lower():
                    print(f"    {k}: {r.get(k)}")

if __name__ == "__main__":
    find_every_gigavis_v2()
