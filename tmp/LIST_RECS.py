import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def list_recs(name, date_str):
    print(f"--- Listing {name} for {date_str} ---")
    try:
        # Fetch without filter first to see what's there
        recs = pb_utils.query_pb(name, limit=20, sort="-date")
        for r in recs:
            if date_str in r['date']:
                print(f"  ID: {r['id']} | Date: {r['date']} | Ticker: {r['ticker']}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    list_recs("vcp_reports", "2026-03-19")
