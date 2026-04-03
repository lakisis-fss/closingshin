import os
import sys
import pandas as pd

# Add the Scripts directory to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Scripts"))
from pb_utils import get_pb_client

def check_migration():
    # 1. Local File Count
    price_dir = r"e:\Downloads\Antigravity Project\ClosingSHIN\Scripts\data\prices"
    csv_files = [f for f in os.listdir(price_dir) if f.endswith('.csv')]
    print(f"Local CSV files count: {len(csv_files)}")

    # 2. PB Collection Counts
    client = get_pb_client()
    
    ohlcv_res = client.collection("ohlcv").get_list(page=1, per_page=1)
    print(f"PocketBase 'ohlcv' record count: {ohlcv_res.total_items}")
    
    stock_info_res = client.collection("stock_infos").get_list(page=1, per_page=1)
    print(f"PocketBase 'stock_infos' record count: {stock_info_res.total_items}")

    # 3. Sample Data Integrity (Samsung Electronics 005930)
    ticker = "005930"
    local_path = os.path.join(price_dir, f"{ticker}.csv")
    
    if os.path.exists(local_path):
        local_df = pd.read_csv(local_path)
        print(f"\nLocal data for {ticker} (Last 5 rows):")
        print(local_df.tail())
        
        pb_ohlcv = client.collection("ohlcv").get_list(
            page=1, per_page=5,
            query_params={"filter": f'code="{ticker}"', "sort": "-date"}
        )
        print(f"\nPocketBase data for {ticker} (Latest 5 rows):")
        for item in pb_ohlcv.items:
            print(f"Date: {item.date}, Close: {item.close}")
    else:
        print(f"\nLocal file for {ticker} not found.")

if __name__ == "__main__":
    check_migration()
