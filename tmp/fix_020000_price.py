from pocketbase import PocketBase
import os

pb = PocketBase('http://127.0.0.1:8090')
iso_date = "2026-03-19 00:00:00.000Z"
ticker = "020000"
correct_price = 25300

try:
    print(f"Update HanSum (020000) for {iso_date} to {correct_price}")
    # Search for ALL records to be safe
    r = pb.collection('stock_infos').get_list(1, 10, {
        "filter": f'ticker = "{ticker}" && date = "{iso_date}"'
    })
    
    if not r.items:
        print("No matching record found. Creating new...")
        pb.collection('stock_infos').create({
            "ticker": ticker,
            "date": iso_date,
            "close": correct_price,
            "name": "한섬"
        })
    else:
        for item in r.items:
            print(f"Updating record ID: {item.id} (Old Close: {item.close})")
            pb.collection('stock_infos').update(item.id, {"close": correct_price})
    
    print("Verification and update successful.")

except Exception as e:
    print(f"Error during update: {e}")
