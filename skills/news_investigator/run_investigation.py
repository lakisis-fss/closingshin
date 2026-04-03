import argparse
import os
import csv
import sys
from dotenv import load_dotenv

# Ensure the script can find the src module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src import collector, analyst

def main():
    parser = argparse.ArgumentParser(description='News Investigator Skill')
    parser.add_argument('--input', required=True, help='Path to VCP CSV input file')
    parser.add_argument('--output', required=True, help='Path to output CSV file')
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    
    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print("Error: NAVER API credentials not found in .env")
        return
    
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not found in .env")
        return

    # 1. Collect News
    print("Step 1: Collecting News...")
    news_data = collector.collect_news(args.input, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)
    
    if not news_data:
        print("No news collected or error occurred.")
        return

    # 2. Analyze News
    print("Step 2: Analyzing News with AI...")
    final_results = analyst.analyze_news_list(news_data, GOOGLE_API_KEY)

    # 3. Save Results
    if final_results:
        print(f"Step 3: Saving {len(final_results)} results to {args.output}...")
        
        # Determine all fieldnames from the data keys
        fieldnames = set()
        for item in final_results:
            fieldnames.update(item.keys())
        fieldnames = list(fieldnames)
        
        # Ensure 'ticker', 'name' are first for readability
        priority_fields = ['ticker', 'name', 'title', 'score', 'trading_signal', 'sentiment_score']
        for p in reversed(priority_fields):
            if p in fieldnames:
                fieldnames.insert(0, fieldnames.pop(fieldnames.index(p)))

        with open(args.output, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(final_results)
        print("Done.")
    else:
        print("No results to save.")

if __name__ == "__main__":
    main()
