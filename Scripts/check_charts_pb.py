from pb_utils import get_pb_token, PB_URL
import requests

def check_migration_status():
    token = get_pb_token()
    if not token:
        print("토큰 획득 실패")
        return

    url = f"{PB_URL}/api/collections/vcp_charts/records"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if r.ok:
        data = r.json()
        total = data.get("totalItems", 0)
        print(f"전체 차트 레코드 수: {total}")
        for item in data.get("items", []):
            print(f"- {item['date']} | {item.get('name', 'N/A')} ({item.get('ticker', 'N/A')}) | {item.get('file', 'N/A')}")
    else:
        print(f"조회 실패: {r.status_code}")
        print(f"오류 내용: {r.text}")

if __name__ == "__main__":
    check_migration_status()
