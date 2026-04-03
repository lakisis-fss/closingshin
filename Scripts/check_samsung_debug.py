
import pb_utils
import json

def check_samsung():
    ticker = "005930"
    recs = pb_utils.query_pb("ohlcv", filter_str=f'code="{ticker}"', sort="-date", limit=10)
    print(f"Latest 10 records for {ticker}:")
    for r in recs:
        print(f"  {r['date']} - Close: {r['close']}")

if __name__ == "__main__":
    check_samsung()
