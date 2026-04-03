from pb_utils import query_pb, delete_pb
from datetime import datetime

def clear_vcp_data():
    date = "2026-03-18 00:00:00.000Z"
    records = query_pb("vcp_reports", filter_str=f'date="{date}"', limit=200)
    print(f"Found {len(records)} records to delete.")
    for r in records:
        delete_pb("vcp_reports", r['id'])
    print("Done clearing.")

if __name__ == "__main__":
    clear_vcp_data()
