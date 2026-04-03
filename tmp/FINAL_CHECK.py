import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils
from collections import Counter

def check_duplicates():
    print("--- Final Duplicate Check (vcp_reports, 2026-03-19) ---")
    try:
        recs = pb_utils.query_pb("vcp_reports", filter_str='date ~ "2026-03-19"', limit=1000)
        print(f"Total retrieved: {len(recs)}")
        
        tickers = [r['ticker'] for r in recs]
        counts = Counter(tickers)
        duplicates = {t: c for t, c in counts.items() if c > 1}
        
        if not duplicates:
            print("  SUCCESS: No duplicates found for 2026-03-19!")
        else:
            print(f"  FAILURE: Found duplicates: {duplicates}")
            
        # Check format
        formats = set([r['date'] for r in recs])
        print(f"  Found date formats: {formats}")
        
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    check_duplicates()
