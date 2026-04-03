import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def test_filter(date_val):
    formatted_date = f"{date_val[:4]}-{date_val[4:6]}-{date_val[6:8]}"
    
    filters = [
        f'date ~ "{formatted_date}"',
        f'date >= "{formatted_date} 00:00:00" && date <= "{formatted_date} 23:59:59"',
        f'date >= "{formatted_date} 00:00:00.000Z" && date <= "{formatted_date} 23:59:59.999Z"'
    ]
    
    for f in filters:
        recs = pb_utils.query_pb("vcp_reports", filter_str=f, limit=5)
        print(f"Filter: {f} -> [{len(recs)} records]")
        if recs:
            print(f" Sample: {recs[0]['ticker']} on {recs[0]['date']}")

if __name__ == "__main__":
    test_filter("20260320")
