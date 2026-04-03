import pandas as pd
import pb_utils as pbu
# Copying _fetch_ohlcv_for_target from 02_scan_vcp.py
def debug_fetch(ticker, name, market_name, start_date, end_date):
    df = pbu.fetch_pb_ohlcv(ticker, limit=100)
    print(f"Fetched {len(df)} rows for {ticker}")
    if df.empty: return "Empty DF"
    
    # We need to set index to 'date' for slicing
    # df.index is ALREADY date if using fetch_pb_ohlcv (wait, I removed set_index, so it's a column)
    if 'date' in df.columns:
        df = df.set_index('date')
    
    print(f"Indices sample: {df.index[:3]}")

    s_dt = pd.to_datetime(start_date)
    e_dt = pd.to_datetime(end_date)
    print(f"Slicing from {s_dt} to {e_dt}")
    
    # Check if index has timezone
    if df.index.tz is not None:
        if s_dt.tzinfo is None:
            s_dt = s_dt.tz_localize(df.index.tz)
        if e_dt.tzinfo is None:
            e_dt = e_dt.tz_localize(df.index.tz)
    
    try:
        ohlcv = df.loc[s_dt:e_dt]
    except Exception as e:
        print(f"Slice error: {e}")
        return "Slice error"
    
    print(f"Sliced records count: {len(ohlcv)}")
    if not ohlcv.empty:
        print(f"First close: {ohlcv['close'].iloc[0]}, Last close: {ohlcv['close'].iloc[-1]}")
    return ohlcv

res = debug_fetch('005930', 'Samsung', 'KOSPI', '20260101', '20260318')
