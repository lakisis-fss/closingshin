import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def check_date():
    recs = pb_utils.query_pb('vcp_reports', filter_str='date ~ "2026-03-21"', limit=1)
    if recs:
        print(f"[{recs[0]['ticker']}] Date: '{recs[0]['date']}'")
    else:
        print("No records for 2026-03-21")

if __name__ == "__main__":
    check_date()
