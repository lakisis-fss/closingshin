import pb_utils
import json

def check_analysis_fields(date_str):
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    pb_date_full = f"{formatted_date} 00:00:00.000Z"
    
    recs = pb_utils.query_pb("news_analysis", filter_str=f'date="{pb_date_full}"', limit=10)
    for rec in recs:
        print(f"ID: {rec.get('id')}")
        print(f"Ticker: '{rec.get('ticker')}'")
        print(f"Target Stock: '{rec.get('target_stock')}'")
        print(f"Title: {rec.get('title')}")
        print("-" * 20)

if __name__ == "__main__":
    check_analysis_fields("20260327")
