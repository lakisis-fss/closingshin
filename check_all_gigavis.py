import os
import sys
import json

# Add the Scripts directory to the path so we can import pb_utils
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))

import pb_utils

def check_all_gigavis():
    print("Checking for all portfolio records with ticker 420770 (Gigavis)...")
    recs = pb_utils.query_pb("portfolio", filter_str='ticker="420770"')
    
    if not recs:
        print("No records found.")
        return

    print(f"Found {len(recs)} records.")
    for i, rec in enumerate(recs):
        print(f"\n--- Record {i+1} (ID: {rec.get('id')}) ---")
        print(f"Name: {rec.get('name')}")
        print(f"Simulation Data: {json.dumps(rec.get('simulation_data'), indent=2, ensure_ascii=False)}")
        print(f"Buy Price: {rec.get('buyPrice')}")

if __name__ == "__main__":
    check_all_gigavis()
