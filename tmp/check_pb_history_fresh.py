import os
import sys
import json

# Add Scripts to path
sys.path.append(os.path.abspath('Scripts'))
import pb_utils

def check_latest_history():
    print("--- Searching for LATEST record with History in market_status ---")
    try:
        # Sort by date descending
        recs = pb_utils.query_pb('market_status', limit=5, sort='-date')
        if not recs:
            print("No records found.")
            return

        for r in recs:
            data = r.get('data', {})
            # History is likely inside data now
            h = data.get('History', [])
            h_len = len(h)
            
            print(f"ID: {r.get('id')}, Date: {r.get('date')}, History Points: {h_len}")
            if h_len > 0:
                print(f"  [FOUND SUCCESS] Data History len: {h_len}")
                print(f"  [FOUND SUCCESS] First point: {h[0]}")
                break
        else:
            print("No record with history found in the last 5 records.")
            if recs:
                print(f"Latest record keys: {list(recs[0].keys())}")
                print(f"Latest record data keys: {list(recs[0].get('data', {}).keys())}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_latest_history()
