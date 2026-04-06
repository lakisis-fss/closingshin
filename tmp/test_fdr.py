import FinanceDataReader as fdr
import pandas as pd

try:
    df = fdr.StockListing('KRX')
    print("KRX fields:", df.columns.tolist())
    print(df.head())
    
    # Check if we have anything like '관리종목', '시장경보', etc.
    # FDR's KRX listing might have 'Market', 'SecuGroup', 'Kind', 'Status' etc.
except Exception as e:
    print(e)
