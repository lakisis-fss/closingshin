
import os
import sys
import json

# Ensure Scripts is in path
sys.path.append(os.path.join(os.getcwd(), "Scripts"))

import pb_utils

print("--- LISTING ALL SETTINGS ---")
recs = pb_utils.query_pb('settings', limit=100)
if recs:
    for r in recs:
        print(f"ID: {r.get('id')} | Key: {r.get('key')}")
        # If it's market_status, print a bit more
        if r.get('key') == 'market_status':
            print("  [MARKET_STATUS CONTENTS FOUND!]")
else:
    print("No settings found in the collection.")
