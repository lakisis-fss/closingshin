
import pb_utils
import json

def check_vcp_reports():
    date_str = "2026-03-23"
    filter_str = f'date >= "{date_str} 00:00:00.000Z" && date <= "{date_str} 23:59:59.999Z"'
    
    recs = pb_utils.query_pb("vcp_reports", filter_str=filter_str, limit=50)
    print(f"VCP reports for {date_str}: {len(recs)}")
    if recs:
        print("Latest VCP report sample:")
        print(f"  - {recs[0]['name']} ({recs[0]['ticker']}): Score {recs[0]['vcp_score']}")

if __name__ == "__main__":
    check_vcp_reports()
