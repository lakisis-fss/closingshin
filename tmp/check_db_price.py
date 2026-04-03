from pocketbase import PocketBase
import os

pb = PocketBase('http://127.0.0.1:8090')
iso_date = "2026-03-19 00:00:00.000Z"
ticker = "020000"

try:
    # Try stock_infos
    print("Checking stock_infos...")
    r = pb.collection('stock_infos').get_list(1, 10, {
        "filter": f'ticker = "{ticker}" && date = "{iso_date}"'
    })
    for item in r.items:
        print(f"  [stock_infos] Date: {item.date}, Ticker: {item.ticker}, Close: {item.close}")

    # Try vcp_reports
    print("Checking vcp_reports...")
    r = pb.collection('vcp_reports').get_list(1, 10, {
        "filter": f'ticker = "{ticker}" && date = "{iso_date}"'
    })
    for item in r.items:
        print(f"  [vcp_reports] Date: {item.date}, Ticker: {item.ticker}, Close: {item.close}")

except Exception as e:
    print(f"Error: {e}")
