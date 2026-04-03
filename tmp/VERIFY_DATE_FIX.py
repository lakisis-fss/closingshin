import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def verify_fix(dt_str):
    fmt = f"{dt_str[:4]}-{dt_str[4:6]}-{dt_str[6:8]}"
    
    # Original (Broken) Filter
    broken_filter = f'date >= "{fmt} 00:00:00Z" && date <= "{fmt} 23:59:59Z"'
    recs_broken = pb_utils.query_pb("ohlcv", filter_str=broken_filter, limit=5)
    print(f"Broken Filter: {broken_filter}")
    print(f"Found {len(recs_broken)} records")
    
    # Fixed Filter (Option 1: Include milliseconds)
    fixed_filter_1 = f'date >= "{fmt} 00:00:00.000Z" && date <= "{fmt} 23:59:59.999Z"'
    recs_fixed_1 = pb_utils.query_pb("ohlcv", filter_str=fixed_filter_1, limit=5)
    print(f"\nFixed Filter 1 (.000Z): {fixed_filter_1}")
    print(f"Found {len(recs_fixed_1)} records")

    # Fixed Filter (Option 2: Use space instead of Z for lower bound comparison)
    fixed_filter_2 = f'date >= "{fmt} 00:00:00" && date <= "{fmt} 23:59:59"'
    recs_fixed_2 = pb_utils.query_pb("ohlcv", filter_str=fixed_filter_2, limit=5)
    print(f"\nFixed Filter 2 (No Z): {fixed_filter_2}")
    print(f"Found {len(recs_fixed_2)} records")

if __name__ == "__main__":
    verify_fix("20260319")
