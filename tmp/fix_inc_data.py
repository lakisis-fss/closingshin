import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def fix_data():
    ticker = '052860'
    date_iso = '2026-04-23 00:00:00.000Z'
    # 고가 5900, 종가 5810으로 유저 입력값 반영
    payload = {
        'code': ticker,
        'date': date_iso,
        'high': 5900,
        'low': 5360,
        'close': 5810,
        'open': 5510,
        'volume': 56464, # 기존 볼륨 유지
        'change': (5810 - 5400) / 5400 # 등락률 대략 계산
    }
    pb_utils.upsert_to_pb('ohlcv', payload, f'code="{ticker}" && date="{date_iso}"')
    print(f"Success: Corrected {ticker} data for 2026-04-23 to High=5900, Close=5810")

if __name__ == "__main__":
    fix_data()
