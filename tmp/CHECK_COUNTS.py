import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def check_counts(date_str):
    collections = ["vcp_reports", "stock_infos", "news_reports", "news_analysis", "vcp_charts"]
    print(f"--- Counts for {date_str} ---")
    for coll in collections:
        try:
            recs = pb_utils.query_pb(coll, filter_str=f'date ~ "{date_str}"', limit=1)
            # To get true count, we might need a separate function, but query_pb returns up to limit.
            # Let's just fetch with a high limit to see.
            all_recs = pb_utils.query_pb(coll, filter_str=f'date ~ "{date_str}"', limit=1000)
            print(f"{coll}: {len(all_recs)}")
        except Exception as e:
            print(f"{coll}: Error - {e}")

if __name__ == "__main__":
    check_counts("2026-03-22")
    check_counts("2026-03-21")
    check_counts("2026-03-20")
