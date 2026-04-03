import pb_utils

def check_ticker_news(ticker, date_str):
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    pb_date_full = f"{formatted_date} 00:00:00.000Z"
    
    print(f"Checking news for ticker {ticker} on {pb_date_full}")
    
    news = pb_utils.query_pb("news_reports", filter_str=f'ticker="{ticker}" && date="{pb_date_full}"')
    print(f"News count: {len(news)}")
    for n in news:
        print(f"Title: {n.get('title')}")

    analysis = pb_utils.query_pb("news_analysis", filter_str=f'ticker="{ticker}" && date="{pb_date_full}"')
    print(f"Analysis count: {len(analysis)}")
    for a in analysis:
        print(f"Sentiment: {a.get('sentiment_score')}")

if __name__ == "__main__":
    check_ticker_news("040160", "20260327")
