from pocketbase import PocketBase
import os

pb = PocketBase('http://127.0.0.1:8090')
ticker = "020000"

try:
    print(f"Checking all records for {ticker} in stock_infos...")
    r = pb.collection('stock_infos').get_list(1, 100, {
        "filter": f'ticker = "{ticker}"',
        "sort": "-date"
    })
    for item in r.items:
        print(f"  Date: {item.date}, Close: {item.close}")

except Exception as e:
    print(f"Error: {e}")
