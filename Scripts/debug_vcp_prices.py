from pb_utils import get_pb_token, PB_URL
import requests
import json

def check_vcp_data():
    token = get_pb_token()
    if not token:
        print("토큰 획득 실패")
        return

    # 2026-03-18 00:00:00.000Z 형식의 날짜로 필터링
    date_filter = "2026-03-18 00:00:00.000Z"
    url = f"{PB_URL}/api/collections/vcp_reports/records"
    params = {
        "filter": f'date = "{date_filter}"',
        "limit": 5
    }
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params)
    if r.ok:
        data = r.json()
        print(f"Total found: {data.get('totalItems')}")
        for item in data.get("items", []):
            print(f"Name: {item.get('name')}, Ticker: {item.get('ticker')}, Close: {item.get('close')}")
            # print(json.dumps(item, indent=2, ensure_ascii=False))
    else:
        print(f"조회 실패: {r.status_code}, {r.text}")

if __name__ == "__main__":
    check_vcp_data()
