from pocketbase import PocketBase
import os

pb = PocketBase('http://127.0.0.1:8090')
iso_date = "2026-03-19 00:00:00.000Z"
ticker = "020000"

try:
    print(f"Checking vcp_reports for {ticker} on {iso_date}")
    r = pb.collection('vcp_reports').get_list(1, 1, {
        "filter": f'ticker = "{ticker}" && date = "{iso_date}"'
    })
    if r.items:
        print(f"Found: Ticker: {r.items[0].ticker}, Close: {r.items[0].close}")
    else:
        print("No record found in vcp_reports.")
except Exception as e:
    print(f"Error: {e}")
