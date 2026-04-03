import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def check_latest():
    collections = ["vcp_reports", "stock_infos", "news_reports", "news_analysis", "vcp_charts"]
    print("--- Latest Records in PB ---")
    for coll in collections:
        try:
            recs = pb_utils.query_pb(coll, sort="-created", limit=1)
            if recs:
                r = recs[0]
                print(f"{coll}: Ticker={r.get('ticker','N/A')}, Name={r.get('name','N/A')}, Date={r.get('date','N/A')}, Created={r.get('created','N/A')}")
            else:
                print(f"{coll}: No records")
        except Exception as e:
            print(f"{coll}: Error - {e}")

if __name__ == "__main__":
    check_latest()
