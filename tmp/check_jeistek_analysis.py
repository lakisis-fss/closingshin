import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def check_analysis():
    ticker = '090470'
    target_date = '2026-04-24'
    
    print(f"--- Checking news_analysis for {ticker} on {target_date} ---")
    
    # news_analysis 컬렉션 조회
    analysis_items = pb_utils.query_pb('news_analysis', filter_str=f'ticker="{ticker}" && date~"{target_date}"')
    print(f"Found {len(analysis_items)} analysis results in 'news_analysis' collection.")
    for item in analysis_items:
        print(f"  - [{item.get('date')}] Label: {item.get('sentiment_label')}")
        print(f"    Score: {item.get('sentiment_score')}")
        print(f"    Title: {item.get('title')}")
        print(f"    Reason: {item.get('reason')}")

if __name__ == "__main__":
    check_analysis()
