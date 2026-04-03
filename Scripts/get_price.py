import sys
import os
import json

# Add Scripts directory to path for pb_utils
sys.path.append(os.path.join(os.path.dirname(__file__)))
import pb_utils

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Ticker required"}))
        return

    ticker = sys.argv[1].zfill(6)
    date_str = sys.argv[2] if len(sys.argv) > 2 else None # YYYYMMDD
    
    try:
        data = {"ticker": ticker, "high": None, "low": None, "close": None, "date": date_str or today_str}
        
        # 1. If date is provided (historical), check 'ohlcv' collection first
        if date_str:
            try:
                # Use pb_utils to query efficiently
                iso_date_start = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} 00:00:00.000Z"
                iso_date_end = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} 23:59:59.999Z"
                
                # We need direct PB client for specific query if pb_utils doesn't have a direct "get_one_day"
                from pocketbase import PocketBase
                pb = PocketBase(os.getenv("PB_URL", "http://127.0.0.1:8090"))
                
                result = pb.collection("ohlcv").get_list(1, 1, {
                    "filter": f'code = "{ticker}" && date >= "{iso_date_start}" && date <= "{iso_date_end}"',
                    "sort": "-date"
                })
                
                if result.items:
                    rec = result.items[0]
                    data["high"] = float(rec.high)
                    data["low"] = float(rec.low)
                    data["close"] = float(rec.close)
            except Exception as e:
                pass

        # 2. If data is still missing (today or not in PB), try real-time or FDR
        if data["close"] is None:
            # Try Naver for real-time (includes high/low for today)
            try:
                import requests
                url = f"https://polling.finance.naver.com/api/realtime?query=SERVICE_ITEM:{ticker}"
                res = requests.get(url, timeout=3)
                if res.status_code == 200:
                    json_res = res.json()
                    if json_res.get('resultCode') == 'success':
                        item = json_res['result']['areas'][0]['datas'][0]
                        # nv: current/close, hv: high, lv: low
                        data["close"] = float(item['nv']) if item.get('nv') is not None else None
                        data["high"] = float(item['hv']) if item.get('hv') is not None else None
                        data["low"] = float(item['lv']) if item.get('lv') is not None else None
            except: pass

        # 3. Final fallback to pb_utils synchronized price (mostly close)
        if data["close"] is None:
            data["close"] = pb_utils.get_synchronized_price(ticker)
            
        print(json.dumps(data))
    except Exception as e:
        print(json.dumps({"error": str(e), "ticker": ticker}))

if __name__ == "__main__":
    main()
