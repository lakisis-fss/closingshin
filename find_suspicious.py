import os
import sys
import json

# Add the Scripts directory to the path so we can import pb_utils
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))

import pb_utils

def find_suspicious_portfolio():
    print("Fetching portfolio records...")
    # Get all records using limit 500 or more if needed
    all_recs = pb_utils.query_pb("portfolio")
    
    if not all_recs:
        print("No records found.")
        return

    print(f"Sample record keys: {list(all_recs[0].keys())}")
    
    suspicious = []
    for rec in all_recs:
        # Based on my previous findings, it might be simulation or simulation_data
        # Let's check both
        sim = rec.get('simulation_data') or rec.get('simulation')
        
        if isinstance(sim, str):
            try:
                sim = json.loads(sim)
            except:
                continue
        
        if not isinstance(sim, dict):
            continue
            
        pnl_pct = sim.get('realizedPnlPercent', 0)
        # If the key is different, check other common names
        if pnl_pct == 0:
            pnl_pct = sim.get('realized_pnl_percent', 0) or sim.get('pnl_percent', 0)
            
        if pnl_pct > 30: 
            suspicious.append({
                "id": rec.get('id'),
                "ticker": rec.get('ticker'),
                "name": rec.get('name'),
                "pnl_pct": pnl_pct,
                "exitPrice": sim.get('exitPrice'),
                "exitDate": sim.get('exitDate')
            })
            
    print(f"\nFound {len(suspicious)} suspicious records:")
    print(json.dumps(suspicious, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    find_suspicious_portfolio()
