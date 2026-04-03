import os
import sys
import json

# Add the Scripts directory to the path so we can import pb_utils
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))

import pb_utils

def fix_gigavis_pnl():
    record_id = "fqktbgog6xy4089" # Gigavis (Correct ID)
    ticker = "420770"
    
    print(f"Fetching record {record_id} for Gigavis...")
    recs = pb_utils.query_pb("portfolio", filter_str=f'id="{record_id}"')
    if not recs:
        print("Record not found.")
        return
        
    rec = recs[0]
    buy_price = rec.get("buyPrice", 77300)
    quantity = rec.get("quantity", 30)
    
    new_exit_price = 79700
    new_pnl_percent = (new_exit_price - buy_price) / buy_price * 100
    new_pnl = (new_exit_price * quantity) - (buy_price * quantity)
    
    print(f"Old Exit Price: {rec.get('simulation_data', {}).get('exitPrice')}")
    print(f"New Exit Price: {new_exit_price}")
    print(f"Estimated PnL: {new_pnl:,.0f} KRW ({new_pnl_percent:.2f}%)")
    
    # Prepare update data
    sim_data = rec.get("simulation_data", {}).copy()
    sim_data.update({
        "exitPrice": new_exit_price,
        "realizedPnl": int(new_pnl),
        "realizedPnlPercent": float(new_pnl_percent),
        "lastUpdate": pb_utils.datetime.now().isoformat()
    })
    
    payload = {
        "simulation_data": sim_data
    }
    
    # Update PocketBase
    success = pb_utils.update_pb("portfolio", record_id, payload)
    if success:
        print("Successfully updated Gigavis portfolio record.")
    else:
        print("Failed to update record.")

if __name__ == "__main__":
    fix_gigavis_pnl()
