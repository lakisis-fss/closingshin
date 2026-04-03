from pb_utils import get_pb_token, PB_URL
import requests
import json

def check_daeju_vcp():
    token = get_pb_token()
    ticker = "078600"
    date = "2026-03-18 00:00:00.000Z"
    
    url_vcp = f"{PB_URL}/api/collections/vcp_reports/records"
    params_vcp = {"filter": f'ticker="{ticker}" && date="{date}"'}
    r_vcp = requests.get(url_vcp, headers={"Authorization": f"Bearer {token}"}, params=params_vcp)
    
    if r_vcp.ok:
        data = r_vcp.json()
        if data["items"]:
            item = data["items"][0]
            print(json.dumps(item, indent=2, ensure_ascii=False))
        else:
            print("No VCP report for Daeju on 2026-03-18")
    else:
        print(f"Error: {r_vcp.status_code}")

if __name__ == "__main__":
    check_daeju_vcp()
