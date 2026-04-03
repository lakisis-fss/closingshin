import sys
import argparse
import json
import logging
import os
from datetime import datetime, timedelta
import pb_utils
import FinanceDataReader as fdr

# 파이썬 출력 인코딩을 강제로 UTF-8로 설정
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Karpathy Skill: Clean, direct, focus on PB as the source
def main():
    parser = argparse.ArgumentParser(description='Get historical price data (PB Only)')
    parser.add_argument('--ticker', type=str, required=True, help='Stock Ticker')
    parser.add_argument('--start_date', type=str, required=True, help='Start date (YYYYMMDD)')
    parser.add_argument('--end_date', type=str, help='End date (YYYYMMDD), optional')
    args = parser.parse_args()

    ticker = args.ticker
    start_date = args.start_date
    end_date = args.end_date
    
    # PocketBase date format conversion
    pb_start = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
    pb_end = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}" if end_date else datetime.now().strftime('%Y-%m-%d')

    try:
        # PB에서 데이터 수집 (Primary Source) - end_date 전달 추가
        df = pb_utils.fetch_pb_ohlcv(ticker, start_date=pb_start, end_date=pb_end)
        
        # PB에 데이터가 없는 경우 FinanceDataReader(FDR)를 Fallback으로 사용
        if df is None or df.empty:
            df = fdr.DataReader(ticker, pb_start, pb_end)
            # Rename for consistency if FDR is used
            df = df.rename(columns={
                'Open': 'open', 'High': 'high', 'Low': 'low', 
                'Close': 'close', 'Volume': 'volume'
            })
        
        if df.empty:
            print(json.dumps({'error': 'No data found in PB or FDR', 'history': []}))
            return

        # 결과를 JSON 배열 형식으로 변환 (기존 인터페이스 유지)
        history = []
        for idx, row in df.iterrows():
            if isinstance(idx, datetime):
                date_str = idx.strftime('%Y-%m-%d')
            else:
                date_str = str(idx).split(' ')[0]

            history.append({
                'date': date_str,
                'open': int(row.get('open') or row.get('Open') or 0),
                'high': int(row.get('high') or row.get('High') or 0),
                'low': int(row.get('low') or row.get('Low') or 0),
                'close': int(row.get('close') or row.get('Close') or 0),
                'volume': int(row.get('volume') or row.get('Volume') or 0)
            })

        print(json.dumps({'history': history}, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({'error': str(e), 'history': []}))


if __name__ == '__main__':
    main()
