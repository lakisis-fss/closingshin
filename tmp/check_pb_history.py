import os
import sys
import json

# Add Scripts to path
sys.path.append(os.path.abspath('Scripts'))
import pb_utils

def deep_check():
    print("--- Searching for History in market_status (Last 50 records) ---")
    try:
        recs = pb_utils.query_pb('market_status', limit=50, sort='-date')
        if not recs:
            print("No records found.")
            return

        found_any = False
        for r in recs:
            keys = list(r.keys())
            history = r.get('History')
            # Handle potential nested 'data' field or direct fields
            h_len = len(history) if isinstance(history, list) else 0
            
            # Also check inside 'data' field if exists
            data_field = r.get('data')
            if isinstance(data_field, dict) and 'History' in data_field:
                h_len = len(data_field['History'])
            
            if h_len > 0:
                print(f"ID: {r.get('id')}, Date: {r.get('date')}, History Points: {h_len} (Keys: {keys})")
                found_any = True
                break
        
        if not found_any:
            print("Finished searching 50 records. No History found in ANY of them.")
            print(f"Sample keys from latest record: {list(recs[0].keys())}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    deep_check()
