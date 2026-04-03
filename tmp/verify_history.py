import sys
import os
import json

# Add Scripts directory to path
sys.path.append(os.path.abspath('Scripts'))
import pb_utils

def verify():
    print("--- Checking market_status collection for LATEST History data ---")
    # Sort by date descending to see most recent
    recs = pb_utils.query_pb('market_status', limit=1, sort='-date')
    if not recs:
        print("Error: No records found in 'market_status'.")
        return
        
    status = recs[0]
    history = status.get('History', [])
    print(f"Latest record date: {status.get('date')}")
    print(f"History length: {len(history)}")
    
    if len(history) > 0:
        print("Sample point:", json.dumps(history[0], indent=2))
        print("Success: History data is present and ready for the graph.")
    else:
        print("Warning: History is still empty.")

if __name__ == "__main__":
    verify()
