from pb_utils import get_pb_token, PB_URL
import requests
import json

def check_all_vcp():
    token = get_pb_token()
    date = "2026-03-18 00:00:00.000Z"
    url = f"{PB_URL}/api/collections/vcp_reports/records"
    params = {"filter": f'date="{date}"', "limit": 100}
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params)
    if r.ok:
        data = r.json()
        print(f"Total: {data['totalItems']}")
        for item in data['items']:
            print(f"Ticker: {item['ticker']}, Name: {item['name']}, Price: {item['price']}")
    else:
        print(f"Error: {r.status_code}")

if __name__ == "__main__":
    check_all_vcp()
