import pb_utils
import json

def check_content(date_str):
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    pb_date_full = f"{formatted_date} 00:00:00.000Z"
    
    print(f"Checking content for {pb_date_full}")
    
    analysis_recs = pb_utils.query_pb("news_analysis", filter_str=f'date="{pb_date_full}"', limit=5)
    for rec in analysis_recs:
        print(f"Name: {rec.get('target_stock')}")
        print(f"Title: {rec.get('title')}")
        print(f"Score: {rec.get('sentiment_score')}")
        print(f"Label: {rec.get('sentiment_label')}")
        print("-" * 20)

    # Check news_reports as well
    news_recs = pb_utils.query_pb("news_reports", filter_str=f'date="{pb_date_full}"', limit=5)
    for rec in news_recs:
        print(f"News - Ticker: {rec.get('ticker')}, Name: {rec.get('name')}, Title: {rec.get('title')}")

if __name__ == "__main__":
    check_content("20260327")
