import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def check_results(dt_str):
    fmt = f"{dt_str[:4]}-{dt_str[4:6]}-{dt_str[6:8]}"
    filter_str = f'date >= "{fmt} 00:00:00.000Z" && date <= "{fmt} 23:59:59.999Z"'
    recs = pb_utils.query_pb("vcp_reports", filter_str=filter_str, limit=5)
    print(f"Checking date: {fmt}")
    print(f"Found {len(recs)} scan results in vcp_reports")
    for r in recs:
        print(f"  {r['ticker']} - {r['name']} - Score: {r['vcp_score']}")

if __name__ == "__main__":
    check_results("20260319")
