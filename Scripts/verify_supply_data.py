import pb_utils
import json
from datetime import datetime

def check_stock_info(ticker, date_str):
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} 00:00:00.000Z"
    filter_str = f'ticker="{ticker}" && date="{formatted_date}"'
    r = pb_utils.query_pb('stock_infos', filter_str=filter_str, limit=1)
    if r:
        print(f"Data for {ticker} on {date_str}:")
        print(json.dumps(r[0], indent=2, ensure_ascii=False))
    else:
        print(f"No data found for {ticker} on {date_str}")

if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "294630"
    check_stock_info(ticker, "20260319")
