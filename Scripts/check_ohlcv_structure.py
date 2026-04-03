from pb_utils import get_pb_token, PB_URL
import requests
import json

def check_ohlcv_record():
    token = get_pb_token()
    url = f"{PB_URL}/api/collections/ohlcv/records"
    params = {"perPage": 1, "sort": "-date"}
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params)
    if r.ok:
        data = r.json()
        if data.get("items"):
            item = data["items"][0]
            print(json.dumps(item, indent=2, ensure_ascii=False))
    else:
        print(f"Error: {r.status_code}")

if __name__ == "__main__":
    check_ohlcv_record()
