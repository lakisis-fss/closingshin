
import pb_utils
import json

def check_data():
    date_str = "2026-03-23"
    filter_str = f'date >= "{date_str} 00:00:00.000Z" && date <= "{date_str} 23:59:59.999Z"'
    print(f"Checking data for {date_str} with filter: {filter_str}")
    
    recs = pb_utils.query_pb("ohlcv", filter_str=filter_str, limit=50)
    print(f"Found {len(recs)} records")
    
    if recs:
        print("First record sample:")
        print(json.dumps(recs[0], indent=2, default=str))
    else:
        # If no records found with Z, try without Z
        filter_str_no_z = f'date >= "{date_str} 00:00:00" && date <= "{date_str} 23:59:59"'
        print(f"Checking data for {date_str} with filter (no Z): {filter_str_no_z}")
        recs_no_z = pb_utils.query_pb("ohlcv", filter_str=filter_str_no_z, limit=50)
        print(f"Found {len(recs_no_z)} records (no Z)")
        if recs_no_z:
            print("First record sample (no Z):")
            print(json.dumps(recs_no_z[0], indent=2, default=str))

if __name__ == "__main__":
    check_data()
