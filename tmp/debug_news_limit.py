import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def debug_limit():
    target_date = '2026-04-24'
    ticker = '090470'
    
    print(f"--- Debugging news limit for {target_date} ---")
    
    # 1. 4월 24일 전체 뉴스(최대 1000개) 가져오기
    all_news = pb_utils.query_pb('news_reports', filter_str=f'date~"{target_date}"', limit=1000)
    print(f"Total news articles collected in 'news_reports': {len(all_news)}")
    
    # 2. 제이스텍 뉴스들의 인덱스 확인
    jeistek_indices = [i for i, n in enumerate(all_news) if n.get('ticker') == ticker]
    print(f"Jeistek news indices in the list: {jeistek_indices}")
    
    if not jeistek_indices:
        print("CRITICAL: Jeistek news NOT FOUND in 'news_reports' for this date.")
        # 혹시 ticker가 '90470' (앞의 0이 빠짐)으로 저장되었는지 확인
        jeistek_indices_alt = [i for i, n in enumerate(all_news) if n.get('ticker') == '90470']
        print(f"Jeistek news indices (alt ticker '90470'): {jeistek_indices_alt}")
    else:
        for idx in jeistek_indices:
            if idx >= 100:
                print(f"Warning: News at index {idx} was SKIPPED by 'limit=100' in 05_analyze_news.py")
            else:
                print(f"News at index {idx} should have been analyzed.")

if __name__ == "__main__":
    debug_limit()
