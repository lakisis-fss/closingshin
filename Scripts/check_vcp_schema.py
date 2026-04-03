from pb_utils import get_pb_token, PB_URL
import requests
import json

def check_vcp_report_schema():
    token = get_pb_token()
    if not token:
        print("토큰 획득 실패")
        return

    url = f"{PB_URL}/api/collections/vcp_reports/records"
    params = {
        "perPage": 1,
        "sort": "-date"
    }
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params)
    if r.ok:
        data = r.json()
        if data.get("items"):
            item = data["items"][0]
            print("VCP Report Record Sample:")
            print(json.dumps(item, indent=2, ensure_ascii=False))
        else:
            print("데이터 없음")
    else:
        print(f"조회 실패: {r.status_code}")

if __name__ == "__main__":
    check_vcp_report_schema()
