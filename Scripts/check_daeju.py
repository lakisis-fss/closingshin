from pb_utils import get_pb_token, PB_URL
import requests
import json

def check_daeju():
    token = get_pb_token()
    ticker = "078600"
    date = "2026-03-18 00:00:00.000Z"
    
    # Check OHLCV
    url_ohlcv = f"{PB_URL}/api/collections/ohlcv/records"
    params_ohlcv = {"filter": f'code="{ticker}" && date="{date}"'}
    r_ohlcv = requests.get(url_ohlcv, headers={"Authorization": f"Bearer {token}"}, params=params_ohlcv)
    if r_ohlcv.ok:
        data_ohlcv = r_ohlcv.json()
        print("OHLCV for Daeju on 2026-03-18:")
        if data_ohlcv.get("items"):
            print(json.dumps(data_ohlcv["items"][0], indent=2, ensure_ascii=False))
        else:
            print("No OHLCV data found")
            
    # Check VCP result
    url_vcp = f"{PB_URL}/api/collections/vcp_reports/records"
    params_vcp = {"filter": f'ticker="{ticker}" && date="{date}"'}
    r_vcp = requests.get(url_vcp, headers={"Authorization": f"Bearer {token}"}, params=params_vcp)
    if r_vcp.ok:
        data_vcp = r_vcp.json()
        print("\nVCP for Daeju on 2026-03-18:")
        if data_vcp.get("items"):
            print(json.dumps(data_vcp["items"][0], indent=2, ensure_ascii=False))
        else:
            print("No VCP report found")

if __name__ == "__main__":
    check_daeju()
