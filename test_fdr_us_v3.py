import FinanceDataReader as fdr
from datetime import datetime, timedelta

def test_symbol(symbol, name, src=None):
    with open('e:/Downloads/Antigravity Project/ClosingSHIN/test_fdr_us_v3.log', 'a', encoding='utf-8') as f:
        f.write(f"--- {name} ({symbol}, src={src}) ---\n")
        try:
            end = datetime.now().strftime("%Y-%m-%d")
            start = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
            args = [symbol, start, end]
            kwargs = {}
            if src: kwargs['data_source'] = src
            
            df = fdr.DataReader(*args, **kwargs)
            if df.empty:
                f.write("  [Empty DF]\n")
            else:
                f.write(str(df.tail(5)) + "\n")
        except Exception as e:
            f.write(f"  [Error] {e}\n")

import os
if os.path.exists('e:/Downloads/Antigravity Project/ClosingSHIN/test_fdr_us_v3.log'):
    os.remove('e:/Downloads/Antigravity Project/ClosingSHIN/test_fdr_us_v3.log')

test_symbol('^IXIC', 'NASDAQ-Yahoo', src='yahoo')
test_symbol('^SOX', 'SOX-Yahoo', src='yahoo')
test_symbol('^TNX', 'US10Y-Treasury-Yahoo', src='yahoo')
test_symbol('USD/KRW', 'USD/KRW')
test_symbol('CL=F', 'WTI_OIL', src='yahoo')
