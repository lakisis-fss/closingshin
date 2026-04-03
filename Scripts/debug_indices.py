import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
import FinanceDataReader as fdr
import requests
import pb_utils
import math
from bs4 import BeautifulSoup
import time
import warnings
import pytz
import re

warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "market_status")
KST = pytz.timezone('Asia/Seoul')
now_kst = datetime.now(KST)
TODAY = now_kst.strftime("%Y%m%d")

def get_market_indices():
    results = {}
    indices = {
        'KOSPI': 'KS11', 
        'KOSDAQ': 'KQ11', 
        'NASDAQ': '^IXIC', 
        'SOX': '^SOX'
    }
    for name, code in indices.items():
        print(f"Fetching {name}...")
        try:
            df = fdr.DataReader(code)
            if df is not None and not df.empty:
                last_row = df.iloc[-1]
                prev_close = df.iloc[-2]['Close'] if len(df) > 1 else last_row['Close']
                change = last_row['Close'] - prev_close
                change_pct = (change / prev_close) * 100
                results[name] = {
                    'Close': float(last_row['Close']),
                    'Change': float(change),
                    'Change_Pct': round(float(change_pct), 2)
                }
                print(f"  {name} success (FDR)")
                continue
            else:
                print(f"  {name} empty (FDR)")
        except Exception as e: 
            print(f"  {name} failed (FDR): {e}")
        
        if name in ['KOSPI', 'KOSDAQ']:
            print(f"  Trying Naver scraper for {name}...")
            try:
                url_code = 'KOSPI' if name == 'KOSPI' else 'KOSDAQ'
                url = f"https://finance.naver.com/sise/sise_index.naver?code={url_code}"
                res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                res.encoding = 'cp949'
                soup = BeautifulSoup(res.text, 'html.parser')
                
                price_el = soup.select_one("#now_value")
                change_el = soup.select_one("#change_value_and_rate")
                
                if price_el and change_el:
                    price_text = price_el.get_text().replace(',', '')
                    print(f"    Raw price: {price_text}")
                    price = float(price_text)
                    text = change_el.get_text(strip=True)
                    print(f"    Raw change text: {text}")
                    match = re.search(r'([0-9.,-]+)\s+([0-9.,-]+)%', text)
                    if match:
                        change_val = float(match.group(1).replace(',', ''))
                        if "하락" in text: change_val = -change_val
                        change_pct = float(match.group(2).replace(',', ''))
                        if "하락" in text: change_pct = -change_pct
                        
                        results[name] = {
                            'Close': price,
                            'Change': change_val,
                            'Change_Pct': change_pct
                        }
                        print(f"    {name} success (Scraper)")
                else:
                    print("    Price/Change EL not found")
            except Exception as e:
                print(f"    {name} scraper error: {e}")
    return results

if __name__ == "__main__":
    indices = get_market_indices()
    print(f"Final Indices: {list(indices.keys())}")
