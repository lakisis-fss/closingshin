from pykrx import stock

tickers = ["189300", "189380"]

for ticker in tickers:
    try:
        name = stock.get_market_ticker_name(ticker)
        print(f"Ticker: {ticker}, Name: {name}")
    except Exception as e:
        print(f"Ticker: {ticker}, Error: {str(e)}")
