import os
import sys

# Add Scripts to path
sys.path.append(os.path.join(os.getcwd(), "Scripts"))
from pb_utils import get_pb_client

def sample_stock_infos():
    client = get_pb_client()
    res = client.collection("stock_infos").get_list(page=1, per_page=20)
    
    print("--- Stock Infos Sampling ---")
    for item in res.items:
        ticker = getattr(item, 'ticker', 'N/A')
        name = getattr(item, 'name', 'N/A')
        market = getattr(item, 'market', 'N/A')
        print(f"Ticker: [{ticker}], Name: {name}, Market: {market}")

if __name__ == "__main__":
    os.chdir(r"e:\Downloads\Antigravity Project\ClosingSHIN")
    sample_stock_infos()
