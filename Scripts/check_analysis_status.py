import os
import sys
# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pb_utils

# Windows Console Encoding Fix
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def check_analysis_status():
    print("\n--- [News Analysis Status Report] ---")
    
    # 1. Total count
    try:
        all_analysis = pb_utils.query_pb("news_analysis", limit=1000)
        print(f"Total News Analysis items: {len(all_analysis)}")
        
        if all_analysis:
            unique_dates = sorted(list(set([r.get('date', 'N/A') for r in all_analysis])), reverse=True)
            print(f"Latest unique dates in news_analysis: {unique_dates[:10]}")
            
            # 2. Check for 036170 specifically (Any date)
            target_ticker = "036170"
            ticker_data = [r for r in all_analysis if str(r.get('ticker', '')).zfill(6) == target_ticker]
            print(f"\nFound {len(ticker_data)} analysis items for ticker {target_ticker}")
            
            # 3. Check for 2026-03-27 specifically
            date_match = "2026-03-27"
            date_data = [r for r in all_analysis if date_match in str(r.get('date', ''))]
            print(f"Found {len(date_data)} analysis items for date {date_match}")
            
            if date_data:
                sample = date_data[0]
                print(f"Sample data for {date_match} -> Ticker: {sample.get('ticker')}, Target: {sample.get('target_stock')}, Link: {sample.get('link')[:30]}...")

    except Exception as e:
        print(f"Error checking analysis status: {e}")

if __name__ == "__main__":
    check_analysis_status()
