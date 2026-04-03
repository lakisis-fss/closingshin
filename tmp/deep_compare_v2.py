import os
import sys
import pandas as pd
import json

# Add Scripts to path
sys.path.append(os.path.join(os.getcwd(), "Scripts"))
from pb_utils import get_pb_client

def deep_compare(ticker="005930"):
    price_dir = r"e:\Downloads\Antigravity Project\ClosingSHIN\Scripts\data\prices"
    local_path = os.path.join(price_dir, f"{ticker}.csv")
    
    report = []
    report.append(f"--- Deep Comparison for {ticker} ---")
    
    # 1. Local Data
    if not os.path.exists(local_path):
        report.append(f"Local file {local_path} not found.")
        return report
    
    local_df = pd.read_csv(local_path)
    report.append(f"Local CSV Header: {local_df.columns.tolist()}")
    last_row = local_df.iloc[-1].to_dict()
    report.append(f"Local Last Row: {json.dumps(last_row, default=str)}")
    
    # 2. PocketBase Data
    client = get_pb_client()
    pb_recs = client.collection("ohlcv").get_list(
        page=1, per_page=10,
        query_params={"filter": f'code="{ticker}"', "sort": "-date"}
    )
    
    if not pb_recs.items:
        report.append("No PocketBase records found.")
    else:
        report.append("\nPocketBase Latest Records:")
        for item in pb_recs.items:
            report.append(f"ID: {item.id}, Date: {item.date}, Open: {item.open}, High: {item.high}, Low: {item.low}, Close: {item.close}, Vol: {item.volume}")

    # 3. Check stock_infos
    si_recs = client.collection("stock_infos").get_list(
        page=1, per_page=1,
        query_params={"filter": f'ticker="{ticker}"'}
    )
    if si_recs.items:
        si = si_recs.items[0]
        name = getattr(si, 'name', 'N/A')
        sector = getattr(si, 'sector', 'N/A')
        market = getattr(si, 'market', 'N/A')
        report.append(f"\nStock Info for {ticker}: Name={name}, Sector={sector}, Market={market}")
    else:
        report.append(f"\nNo stock_info record for {ticker}")

    # 4. Identify missing tickers
    csv_files = [f.replace('.csv', '') for f in os.listdir(price_dir) if f.endswith('.csv')]
    all_si = client.collection("stock_infos").get_full_list()
    pb_si_tickers = [getattr(item, 'ticker', '') for item in all_si]
    
    missing_in_pb = set(csv_files) - set(pb_si_tickers)
    report.append(f"\nTickers in CSV but missing in PB stock_infos: {len(missing_in_pb)}")
    if missing_in_pb:
        report.append(f"Examples of missing tickers: {list(missing_in_pb)[:10]}")
    
    return report

if __name__ == "__main__":
    os.chdir(r"e:\Downloads\Antigravity Project\ClosingSHIN")
    results = deep_compare("005930")
    with open("tmp/report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(results))
