import os
import sys

# Add Scripts to path
sys.path.append(os.path.join(os.getcwd(), "Scripts"))
from pb_utils import get_pb_client

def check_ohlcv_tickers():
    client = get_pb_client()
    
    # We can't easily get unique values from PB directly without full list or special query.
    # But we can check total records and maybe sample some tickers.
    # Alternatively, use the 'ohlcv' collection and see total items.
    
    res = client.collection("ohlcv").get_list(page=1, per_page=1)
    total_records = res.total_items
    print(f"Total OHLCV records: {total_records}")
    
    # Let's try to get a sense of unique tickers by listing with a group or just getting some pages.
    # Actually, a better way is to check the CSV files one by one and see if they exist in PB.
    # But that's slow. 
    
    # Let's check if '016250' (one of the missing in stock_infos) has ohlcv data.
    ticker = "016250"
    res = client.collection("ohlcv").get_list(
        page=1, per_page=1,
        query_params={"filter": f'code="{ticker}"'}
    )
    if res.items:
        print(f"Ticker {ticker} has {res.total_items} records in ohlcv.")
    else:
        print(f"Ticker {ticker} has NO records in ohlcv.")

if __name__ == "__main__":
    os.chdir(r"e:\Downloads\Antigravity Project\ClosingSHIN")
    check_ohlcv_tickers()
