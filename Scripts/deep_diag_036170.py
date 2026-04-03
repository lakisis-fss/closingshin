import os
import sys
# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pb_utils

# Windows Console Encoding Fix
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def deep_diag_ticker(target_ticker):
    print(f"\n[Deep Diag] Ticker: {target_ticker}")
    
    # 1. Search in news_reports
    filter_q = f'ticker ~ "{target_ticker}"'
    reports = pb_utils.query_pb("news_reports", filter_str=filter_q, limit=10)
    print(f"\nFound {len(reports)} records in 'news_reports'")
    for r in reports:
        print(f"  ID: {r.get('id')}, Date: {r.get('date')}, Title: {r.get('title')[:30]}...")

    # 2. Search in news_analysis
    analyses = pb_utils.query_pb("news_analysis", filter_str=filter_q, limit=10)
    print(f"\nFound {len(analyses)} records in 'news_analysis'")
    for a in analyses:
        print(f"  ID: {a.get('id')}, Date: {a.get('date')}, Sentiment: {a.get('sentiment_label')}, Reason: {a.get('reason')[:30]}...")

    # 3. Check VCP Reports for this ticker
    vcp_dates = pb_utils.query_pb("vcp_reports", filter_str=filter_q, limit=10)
    print(f"\nFound {len(vcp_dates)} records in 'vcp_reports'")
    for v in vcp_dates:
        print(f"  ID: {v.get('id')}, Date: {v.get('date')}, VCP Score: {v.get('vcp_score')}")

if __name__ == "__main__":
    deep_diag_ticker("036170")
