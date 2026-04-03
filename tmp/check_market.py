import pb_utils
import json
import os

# Ensure Scripts is in path
import sys
sys.path.append(os.path.join(os.getcwd(), "Scripts"))

res = pb_utils.query_pb('settings', filter_str='key="market_status"')
print("--- MARKET STATUS ---")
if res:
    # market_status value is a dict now
    print(json.dumps(res[0], indent=2))
else:
    print("No market_status found.")

res2 = pb_utils.query_pb('settings', filter_str='key="ai_insights"')
print("\n--- AI INSIGHTS ---")
if res2:
    print(json.dumps(res2[0], indent=2))
else:
    print("No ai_insights found.")
