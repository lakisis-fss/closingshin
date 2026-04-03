import os
import sys
import json

# Add Scripts to path
sys.path.append(os.path.abspath('Scripts'))
import pb_utils

def check_settings():
    print("--- Checking settings collection for market_status (Fixed) ---")
    try:
        # Correct argument name is filter_str
        recs = pb_utils.query_pb('settings', filter_str='key="market_status"')
        if not recs:
            print("No market_status key found in settings.")
            return

        r = recs[0]
        # PocketBase SDK 0.25+ Record object might have attributes directly
        # But pb_utils.query_pb converts it to a dict (copy of __dict__)
        val = r.get('value', {})
        history = val.get('History', [])
        print(f"ID: {r.get('id')}, History length: {len(history)}")
        if len(history) > 0:
            print(f"  [FOUND] History is present! Examples: {history[:2]}")
        else:
            print("  [WARNING] History is still 0. Data keys present: ", list(val.keys()))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_settings()
