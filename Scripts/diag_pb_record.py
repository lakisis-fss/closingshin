import sys
import os
sys.path.append('e:/Downloads/Antigravity Project/ClosingSHIN/Scripts')
import pb_utils

ticker = "323280"
date = "2026-03-19 00:00:00.000Z"
data = pb_utils.query_pb("stock_infos", filter_str=f'ticker="{ticker}" && date="{date}"', limit=1)
if data:
    item = data[0]
    print(f"--- All Keys in Record ---")
    print(sorted(item.keys()))
    print(f"\n--- Specific Values ---")
    # Try multiple possible keys
    for k in ['PER', 'per', 'PBR', 'pbr', 'EPS', 'eps', 'BPS', 'bps', 'DIV', 'div']:
        if k in item:
            print(f"{k}: {item[k]} (Type: {type(item[k])})")
else:
    print("No data found.")
