import sys
import os

# Add current directory to path to import 06 script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from importlib import import_module

# Import the module dynamically since it starts with a number
collect_stock = import_module("06_collect_stock_data")

ticker = "298020" # 효성티앤씨
dates = ["20260211", "20260212", "20260213"]

print(f"Testing get_price_data for {ticker} with fix...")

for date in dates:
    print(f"\n--- Date: {date} ---")
    change, close = collect_stock.get_price_data(ticker, date)
    print(f"Result: Change={change}, Close={close}")
