from pb_utils import get_pb_token, PB_URL
import requests
import json

def check_ohlcv_ticker():
    token = get_pb_token()
    ticker = "006800"
    date = "2026-03-18 00:00:00.000Z"
    url = f"{PB_URL}/api/collections/ohlcv/records"
    params = {"filter": f'code="{ticker}" && date="{date}"'}
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params)
    if r.ok:
        data = r.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"Error: {r.status_code}")

if __name__ == "__main__":
    check_ohlcv_ticker()
