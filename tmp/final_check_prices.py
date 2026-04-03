import yfinance as yf
import pandas as pd

tickers = {
    'KOSPI200': '069500.KS', 
    'SEMICON': '091160.KS', 
    'BATTERY': '305540.KS',
    'AUTO': '091170.KS',
    'IT': '139260.KS',
    'BANK': '091180.KS',
    'STEEL': '117680.KS',
    'SECURITIES': '091190.KS'
}

print("Comparing Close vs Adj Close for all 8 sectors...")
for name, ticker in tickers.items():
    try:
        # Get at least 2 days to check for change too
        df = yf.download(ticker, period='5d', progress=False)
        if not df.empty:
            # yfinance often returns MultiIndex columns
            if isinstance(df.columns, pd.MultiIndex):
                close = df.xs('Close', axis=1, level=0).iloc[-1].item()
                adj_close = df.xs('Adj Close', axis=1, level=0).iloc[-1].item()
            else:
                close = df['Close'].iloc[-1]
                adj_close = df['Adj Close'].iloc[-1]
            
            print(f"[{name}] {ticker}")
            print(f"  Close:     {close:,.0f}")
            print(f"  Adj Close: {adj_close:,.0f}")
    except Exception as e:
        print(f"[{name}] {ticker} Error: {e}")
