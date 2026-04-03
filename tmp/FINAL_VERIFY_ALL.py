import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils
from collections import Counter

def check(name, date_str, ticker_field='ticker'):
    print(f"--- Checking {name} for {date_str} ---")
    try:
        recs = pb_utils.query_pb(name, filter_str=f'date ~ "{date_str}"', limit=2000)
        print(f"  Total: {len(recs)}")
        tickers = [r.get(ticker_field) for r in recs]
        counts = Counter(tickers)
        dups = {t: c for t, c in counts.items() if c > 1}
        print(f"  Duplicates: {dups if dups else 'None'}")
        formats = set([r['date'] for r in recs])
        print(f"  Formats: {formats}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    day = "2026-03-19"
    check("vcp_reports", day, 'ticker')
    check("stock_infos", day, 'ticker')
    check("news", day, 'ticker')
    check("news_analysis", day, 'ticker')
