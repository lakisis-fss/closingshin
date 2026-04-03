import os
import sys
# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pb_utils

# Windows Console Encoding Fix
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def final_check(date_str):
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    print(f"\n[Final Check] Date: {formatted_date}")
    
    # 1. Total count without filter
    try:
        raw_analysis = pb_utils.query_pb("news_analysis", limit=5, sort="-created")
        print(f"Latest 5 analysis records overall:")
        for r in raw_analysis:
            print(f"  Ticker: {r.get('ticker')}, Code: {r.get('code')}, Date: {r.get('date')}, Created: {r.get('created')}")

        # 2. Count for the specific date
        filter_q = f'date ~ "{formatted_date}"'
        search_analysis = pb_utils.query_pb("news_analysis", filter_str=filter_q, limit=5)
        print(f"\nAnalysis records found for {formatted_date}: {len(search_analysis)}")
        
        # 3. Check vcp_reports fields
        vcp_raw = pb_utils.query_pb("vcp_reports", limit=1, sort="-created")
        if vcp_raw:
            print(f"\nVCP Report Sample Fields: {list(vcp_raw[0].keys())}")
            print(f"  Ticker value: {vcp_raw[0].get('ticker')}, Code value: {vcp_raw[0].get('code')}")

    except Exception as e:
        print(f"Error during check: {e}")

if __name__ == "__main__":
    final_check("20260327")
