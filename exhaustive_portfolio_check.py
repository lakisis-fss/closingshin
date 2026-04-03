import os
import sys
import json

# Add the Scripts directory to the path so we can import pb_utils
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))

import pb_utils

def check_all_portfolio():
    print("Listing ALL records in 'portfolio' containing 'Gigavis' or '기가비스'...")
    recs = pb_utils.query_pb("portfolio")
    
    matches = [r for r in recs if "기가비스" in str(r.get('name', '')) or "420770" in str(r.get('ticker', ''))]
    
    print(f"Found {len(matches)} match(es).")
    for r in matches:
        print(f"\nID: {r.get('id')}")
        print(f"Name: {r.get('name')}")
        print(f"Ticker: {r.get('ticker')}")
        print(f"Simulation: {json.dumps(r.get('simulation'), indent=2, ensure_ascii=False)}")
        print(f"Simulation_data: {json.dumps(r.get('simulation_data'), indent=2, ensure_ascii=False)}")
        print(f"Buy Price: {r.get('buy_price')}")

if __name__ == "__main__":
    check_all_portfolio()
