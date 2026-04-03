import sys
import os
sys.path.append('e:/Downloads/Antigravity Project/ClosingSHIN/Scripts')
import pb_utils

ticker = "294630"
date = "2026-03-19 00:00:00.000Z"
data = pb_utils.query_pb('stock_infos', filter_str=f'ticker="{ticker}" && date="{date}"', limit=1)
if data:
    info = data[0]
    print(f"--- Supply Score Verification (V5) ---")
    print(f"Ticker: {info.get('ticker')} ({info.get('name')})")
    print(f"Date:   {info.get('date')}")
    print(f"FINAL SCORE (V5): {info.get('supply_score')}")
    print("-" * 30)
    p_weights = {5: 15, 15: 20, 30: 25, 50: 20, 100: 20}
    for p, w in p_weights.items():
        inst = info.get(f'inst_net_{p}d', 0)
        frgn = info.get(f'foreign_net_{p}d', 0)
        indi = info.get(f'indiv_net_{p}d', 0)
        print(f"{p:>3}D (W:{w}): Inst({inst:>8}), Foreign({frgn:>8}), Indiv({indi:>8})")
else:
    print("No data found.")
