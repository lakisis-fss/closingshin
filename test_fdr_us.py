import FinanceDataReader as fdr
from datetime import datetime, timedelta

def test_symbol(symbol, name, src=None):
    print(f"--- {name} ({symbol}, src={src}) ---")
    try:
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        args = [symbol, start, end]
        kwargs = {}
        if src: kwargs['data_source'] = src
        
        df = fdr.DataReader(*args, **kwargs)
        if df.empty:
            print("  [Empty DF]")
        else:
            print(df.tail(3))
            if len(df) >= 2:
                c1 = df['Close'].iloc[-1]
                c2 = df['Close'].iloc[-2]
                print(f"  Last: {c1}, Prev: {c2}, Change: {c1-c2}")
    except Exception as e:
        print(f"  [Error] {e}")

test_symbol('IXIC', 'NASDAQ-Naver', src='naver')
test_symbol('^IXIC', 'NASDAQ-Yahoo', src='yahoo')
test_symbol('SOX', 'SOX-Naver', src='naver')
test_symbol('^SOX', 'SOX-Yahoo', src='yahoo')
test_symbol('US10YT', 'US10Y-FDR')
test_symbol('FRED:DGS10', 'US10Y-FRED')
