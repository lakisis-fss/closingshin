import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def audit():
    print("--- Auditing vcp_reports ---")
    try:
        recs = pb_utils.query_pb("vcp_reports", filter_str='date ~ "2026-03-19"', limit=100)
        print(f"Total retrieved: {len(recs)}")
        for i, r in enumerate(recs):
            print(f"  {i+1}. ID: {r['id']} | Date: {r['date']} | Ticker: {r['ticker']} | Name: {r.get('name', 'N/A')}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    audit()
