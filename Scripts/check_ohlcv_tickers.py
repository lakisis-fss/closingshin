from pb_utils import query_pb
date = '2026-03-18 00:00:00.000Z'
recs = query_pb('ohlcv', filter_str=f'date="{date}"', limit=5000)
codes = set([r['code'] for r in recs])
print(f"Found {len(codes)} unique tickers in ohlcv for {date}")
