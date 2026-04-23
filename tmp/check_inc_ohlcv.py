import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils
import json
from datetime import datetime

def check_inc_data():
    # 1. 아이엔씨 티커 확인 (부분 일치 검색)
    stocks = pb_utils.query_pb("stock_infos", filter_str='name ~ "아이엔씨"', limit=5)
    if not stocks:
        print("아이엔씨 키워드로 종목을 찾을 수 없습니다.")
        # 전체 리스트에서 비슷한 게 있는지 확인하기 위해 상위 10개 출력
        all_stocks = pb_utils.query_pb("stock_infos", limit=10)
        print("DB 내 상위 10개 종목 예시:", [s['name'] for s in all_stocks])
        return
    
    ticker = stocks[0]['ticker']
    name = stocks[0]['name']
    print(f"종목명: {name}, 티커: {ticker}")

    # 2. 4월 23일 OHLCV 데이터 확인
    target_date = "2026-04-23"
    filter_str = f'code="{ticker}" && date >= "{target_date} 00:00:00.000Z" && date <= "{target_date} 23:59:59.999Z"'
    ohlcv = pb_utils.query_pb("ohlcv", filter_str=filter_str, limit=1)
    
    if ohlcv:
        print("\n--- DB에 저장된 4월 23일 OHLCV ---")
        print(json.dumps(ohlcv[0], indent=2, ensure_ascii=False))
    else:
        print(f"\n{target_date}의 OHLCV 데이터가 DB에 없습니다.")

if __name__ == "__main__":
    check_inc_data()
