import yfinance as yf

sectors = {
    'KOSPI200': '069500', 
    'SEMICON': '091160', 
    'BATTERY': '305540',
    'AUTO': '091170',
    'IT': '139260',
    'BANK': '091180',
    'STEEL': '117680',
    'SECURITIES': '091190'
}

print("Verifying 8 sectors via yfinance...")
for name, code in sectors.items():
    ticker = f"{code}.KS"
    try:
        df = yf.download(ticker, period='5d', progress=False)
        if not df.empty:
            last_price = df['Close'].iloc[-1].item()
            print(f"  [SUCCESS] {name} ({ticker}): {last_price:,.1f}")
        else:
            print(f"  [FAILED] {name} ({ticker}): No data found")
    except Exception as e:
        print(f"  [ERROR] {name} ({ticker}): {e}")
