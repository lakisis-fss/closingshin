import os
import sys
import json

# Add the Scripts directory to the path so we can import pb_utils
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))

import pb_utils

def find_every_gigavis():
    print("Searching for ALL records that might be 'Gigavis' (기가비스)...")
    
    # Search by ticker
    recs_ticker = pb_utils.query_pb("portfolio", filter_str='ticker ~ "420770"')
    # Search by name
    recs_name = pb_utils.query_pb("portfolio", filter_str='name ~ "기가비스"')
    
    # Merge and deduplicate by ID
    all_recs = {r['id']: r for r in recs_ticker + recs_name}
    
    print(f"Found {len(all_recs)} unique records total.")
    
    for rid, rec in all_recs.items():
        print(f"\n[{rid}] Ticker: '{rec.get('ticker')}', Name: '{rec.get('name')}'")
        sim = rec.get('simulation_data')
        if isinstance(sim, str):
            try: sim = json.loads(sim)
            except: pass
            
        if isinstance(sim, dict):
            status = sim.get('status')
            price = sim.get('exitPrice')
            pnl = sim.get('realizedPnlPercent')
            print(f"  Simulation: status={status}, exitPrice={price}, realizedPnlPercent={pnl}%")
        else:
            print(f"  Simulation: {sim}")

if __name__ == "__main__":
    find_every_gigavis()
