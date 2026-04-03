import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def check_ohlcv():
    recs = pb_utils.query_pb("ohlcv", filter_str='code="005930"', sort="-date", limit=10)
    if recs:
        print("--- Latest OHLCV for 005930 ---")
        for r in recs:
            print(f"Date: {r['date']}, Close: {r['close']}")
    else:
        print("No OHLCV for 005930")

if __name__ == "__main__":
    check_ohlcv()
