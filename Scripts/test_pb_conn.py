import pb_utils
import pandas as pd

try:
    token = pb_utils.get_pb_token()
    if token:
        print("PB Connection: SUCCESS")
        # Try to fetch one ticker
        # (Assuming 005930 exists from previous migration steps)
        df = pb_utils.fetch_pb_ohlcv("005930", limit=5, token=token)
        if not df.empty:
            print(f"Data Fetch: SUCCESS ({len(df)} rows)")
            print(df.tail(2))
        else:
            print("Data Fetch: EMPTY (Check if 005930 is migrated)")
    else:
        print("PB Connection: FAILED (Check if PocketBase is running)")
except Exception as e:
    print(f"Error: {e}")
