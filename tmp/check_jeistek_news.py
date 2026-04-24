import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils
from datetime import datetime

def check_data():
    ticker = '090470' # 제이스텍
    target_date = '2026-04-24'
    
    print(f"--- Checking data for {ticker} on {target_date} ---")
    
    # 1. 뉴스 데이터 확인
    news_items = pb_utils.query_pb('news', filter_str=f'ticker="{ticker}" && date~"{target_date}"')
    print(f"Found {len(news_items)} news items in 'news' collection.")
    for item in news_items:
        print(f"  - [{item.get('date')}] {item.get('title')}")
        
    # 2. 분석 리포트 데이터 확인
    report_items = pb_utils.query_pb('news_reports', filter_str=f'ticker="{ticker}" && date~"{target_date}"')
    print(f"\nFound {len(report_items)} analysis reports in 'news_reports' collection.")
    for report in report_items:
        print(f"  - [{report.get('date')}] Sentiment: {report.get('sentiment')}")
        print(f"    Keywords: {report.get('keywords')}")
        
    # 3. 만약 분석 리포트가 없다면, 왜 없을까? 05_analyze_news.py의 필터링 조건 확인을 위해 
    # 전체 뉴스 중 '제이스텍' 키워드가 들어간 다른 뉴스가 있는지 확인
    all_jeistek_news = pb_utils.query_pb('news', filter_str=f'title~"제이스텍" && date~"{target_date}"')
    print(f"\nFound {len(all_jeistek_news)} news items with keyword '제이스텍' (any ticker).")
    for item in all_jeistek_news:
        print(f"  - [{item.get('ticker')}] {item.get('title')}")

if __name__ == "__main__":
    check_data()
