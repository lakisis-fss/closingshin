import os
import sys
import pandas as pd
from datetime import datetime

# Add Scripts to path
sys.path.append(os.path.join(os.getcwd(), "Scripts"))
from pb_utils import get_pb_client

def deep_compare(ticker="005930"):
    price_dir = r"e:\Downloads\Antigravity Project\ClosingSHIN\Scripts\data\prices"
    local_path = os.path.join(price_dir, f"{ticker}.csv")
    
    print(f"--- Deep Comparison for {ticker} ---")
    
    # 1. Local Data
    if not os.path.exists(local_path):
        print(f"Local file {local_path} not found.")
        return
    
    local_df = pd.read_csv(local_path)
    print("Local CSV Header:", local_df.columns.tolist())
    print("Local Last Row:\n", local_df.iloc[-1])
    
    # 2. PocketBase Data
    client = get_pb_client()
    pb_recs = client.collection("ohlcv").get_list(
        page=1, per_page=10,
        query_params={"filter": f'code="{ticker}"', "sort": "-date"}
    )
    
    if not pb_recs.items:
        print("No PocketBase records found.")
        return
    
    print("\nPocketBase Latest Records:")
    for item in pb_recs.items:
        print(f"ID: {item.id}, Date: {item.date}, Open: {item.open}, High: {item.high}, Low: {item.low}, Close: {item.close}, Vol: {item.volume}")

    # 3. Check stock_infos
    si_recs = client.collection("stock_infos").get_list(
        page=1, per_page=1,
        query_params={"filter": f'ticker="{ticker}"'}
    )
    if si_recs.items:
        si = si_recs.items[0]
        print(f"\nStock Info for {ticker}: Name={si.name}, Sector={si.sector}, Market={si.market}")
    else:
        print(f"\nNo stock_info record for {ticker}")

    # 4. Identify missing tickers
    csv_files = [f.replace('.csv', '') for f in os.listdir(price_dir) if f.endswith('.csv')]
    pb_tickers = []
    # To avoid timeout, we query stock_infos in chunks or just get full list if manageable (1621 is fine)
    all_si = client.collection("stock_infos").get_full_list()
    pb_si_tickers = [item.ticker for item in all_si]
    
    missing_in_pb = set(csv_files) - set(pb_si_tickers)
    print(f"\nTickers in CSV but missing in PB stock_infos: {len(missing_in_pb)}")
    if missing_in_pb:
        print("Examples of missing tickers:", list(missing_in_pb)[:10])

if __name__ == "__main__":
    # Ensure we are in the root directory to find Scripts correctly
    os.chdir(r"e:\Downloads\Antigravity Project\ClosingSHIN")
    deep_compare("005930")
