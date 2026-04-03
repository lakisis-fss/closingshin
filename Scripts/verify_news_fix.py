import os
import sys
# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pb_utils

# Windows Console Encoding Fix
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def verify_fix(target_ticker, date_str):
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    # Range filter used in new api.ts
    range_filter = f'date >= "{formatted_date} 00:00:00.000Z" && date <= "{formatted_date} 23:59:59.999Z"'
    
    print(f"\n[Verification] Target: {target_ticker}, Date: {formatted_date}")
    
    # 1. Check news_reports
    print(f"Checking news_reports with range filter...")
    reports = pb_utils.query_pb("news_reports", filter_str=range_filter, limit=100)
    print(f"Total reports found on this date: {len(reports)}")
    
    matched_reports = []
    target_name = "신일전자" # Example name for 036170
    
    for r in reports:
        ticker = str(r.get('ticker', '')).zfill(6)
        name = r.get('name', '')
        if ticker == target_ticker or (target_name in name or name in target_name):
            matched_reports.append(r)
            
    print(f"Matched reports for {target_ticker}: {len(matched_reports)}")
    if matched_reports:
        print(f"  Sample matched news: {matched_reports[0].get('title')}")

    # 2. Check news_analysis
    print(f"\nChecking news_analysis with range filter...")
    analyses = pb_utils.query_pb("news_analysis", filter_str=range_filter, limit=100)
    print(f"Total analyses found on this date: {len(analyses)}")
    
    matched_analyses = []
    for a in analyses:
        ticker = str(a.get('ticker', '')).zfill(6)
        target_stock = a.get('target_stock', '')
        if ticker == target_ticker or (target_name in target_stock or target_stock in target_name):
            matched_analyses.append(a)
            
    print(f"Matched analyses for {target_ticker}: {len(matched_analyses)}")
    if matched_analyses:
        print(f"  Sample matched analysis (reason): {matched_analyses[0].get('reason')}")

if __name__ == "__main__":
    verify_fix("036170", "20260327")
