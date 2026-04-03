import os
import sys
import json

# Add the Scripts directory to the path so we can import pb_utils
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))

import pb_utils

def fix_gigavis_correct_field():
    record_id = "fqktbgog6xy4089"
    ticker = "420770"
    
    print(f"Fetching record {record_id} for Gigavis...")
    # Get the raw record first to be safe
    client = pb_utils.get_pb_client()
    item = client.collection('portfolio').get_one(record_id)
    
    # Buy price and quantity
    buy_price = 77300
    quantity = 30
    
    # Logic from the app
    new_exit_price = 79700
    new_pnl_percent = (new_exit_price - buy_price) / buy_price * 100
    new_pnl = (new_exit_price * quantity) - (buy_price * quantity)
    
    print(f"Updating simulation field for {record_id}...")
    
    # In the SDK, simulation is a dict
    simulation = getattr(item, 'simulation', {})
    if not simulation:
        print("Simulation field was empty, initializing...")
        simulation = {}

    simulation.update({
        "exitPrice": new_exit_price,
        "realizedPnl": int(new_pnl),
        "realizedPnlPercent": float(new_pnl_percent),
        "lastUpdate": pb_utils.datetime.now().isoformat()
    })
    
    # PocketBase SDK update
    data = {
        "simulation": simulation
    }
    
    try:
        updated = client.collection('portfolio').update(record_id, data)
        print("Update successful!")
        print(f"New exitPrice: {updated.simulation.get('exitPrice')}")
        print(f"New realizedPnlPercent: {updated.simulation.get('realizedPnlPercent')}%")
    except Exception as e:
        print(f"Update failed: {e}")

if __name__ == "__main__":
    fix_gigavis_correct_field()
