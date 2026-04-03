
import os
import glob
import pandas as pd
import numpy as np

# Paths
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

# Constants from scoreCalculator.ts
WEIGHTS = {
    'vcp': 0.20,
    'supply': 0.30,
    'sentiment': 0.30,
    'fundamental': 0.10,
    'sector': 0.10,
}

# Function to load and analyze data
def analyze_scores(start_date, end_date):
    print(f"Analyzing scores from {start_date} to {end_date}...")
    
    # Files
    vcp_files = glob.glob(os.path.join(RESULTS_DIR, "vcp_report_*.csv"))
    stock_files = glob.glob(os.path.join(RESULTS_DIR, "stock_info_*.csv"))
    news_files = glob.glob(os.path.join(RESULTS_DIR, "news_analysis_*.csv"))
    
    # Filter by date range
    start_dt = pd.to_datetime(start_date, format='%Y%m%d')
    end_dt = pd.to_datetime(end_date, format='%Y%m%d')
    
    valid_dates = []
    
    # Collect data into lists
    all_vcp_scores = []
    all_supply_scores = []
    all_fund_scores = []
    all_sentiment_raw = []
    all_sentiment_scores = [] # 0-100 scale
    all_total_scores = []
    
    # Iterate through dates
    potential_dates = pd.date_range(start_dt, end_dt).strftime('%Y%m%d').tolist()
    
    for date in potential_dates:
        vcp_path = os.path.join(RESULTS_DIR, f"vcp_report_{date}.csv")
        stock_path = os.path.join(RESULTS_DIR, f"stock_info_{date}.csv")
        news_path = os.path.join(RESULTS_DIR, f"news_analysis_{date}.csv")
        
        # Check if basic VCP file exists
        if not os.path.exists(vcp_path):
            continue
            
        print(f"Processing {date}...")
        
        # Load Dataframes
        try:
            df_vcp = pd.read_csv(vcp_path, dtype={'ticker': str})
            # Ensure ticker is 6 digits
            df_vcp['ticker'] = df_vcp['ticker'].str.zfill(6)
            
            df_stock = pd.DataFrame()
            if os.path.exists(stock_path):
                df_stock = pd.read_csv(stock_path, dtype={'ticker': str})
                df_stock['ticker'] = df_stock['ticker'].str.zfill(6)
                
            df_news = pd.DataFrame()
            if os.path.exists(news_path):
                df_news = pd.read_csv(news_path, dtype={'ticker': str})
                if 'ticker' in df_news.columns:
                     df_news['ticker'] = df_news['ticker'].str.zfill(6)
                elif 'target_stock' in df_news.columns:
                     # Fallback mapping if ticker missing in early versions
                     pass 

        except Exception as e:
            print(f"Error reading files for {date}: {e}")
            continue

        # Merge Data to Calculate Total Score for each ticker
        for _, row in df_vcp.iterrows():
            ticker = row['ticker']
            vcp_s = row.get('vcp_score', 50)
            
            # Find Stock Info
            supply_s = 50
            fund_s = 50
            
            if not df_stock.empty:
                stock_row = df_stock[df_stock['ticker'] == ticker]
                if not stock_row.empty:
                    supply_s = stock_row.iloc[0].get('supply_score', 50)
                    fund_s = stock_row.iloc[0].get('fundamental_score', 50)
            
            # Find Sentiment
            sent_s = 50 # Default 0.0 -> 50
            raw_sent = 0.0
            
            if not df_news.empty and 'sentiment_score' in df_news.columns:
                # Filter news for this ticker
                # Try ticker match first
                news_rows = df_news[df_news['ticker'] == ticker]
                if news_rows.empty and 'name' in row:
                    # Try name match
                    news_rows = df_news[df_news['target_stock'] == row['name']]
                
                if not news_rows.empty:
                    # Calculate Average Sentiment
                    avg_sent = news_rows['sentiment_score'].mean()
                    raw_sent = avg_sent
                    # Convert to 0-100: (raw * 1.5 + 1) * 50 (Amplified Sensitivity)
                    sent_s = (avg_sent * 1.5 + 1) * 50
                    sent_s = max(0, min(100, sent_s))
            
            # Calculate Total
            # VCP 20%, Supply 30%, Sentiment 30%, Fund 10%, Sector 10% (Fixed 50)
            sector_s = 50
            
            total = (vcp_s * 0.2) + (supply_s * 0.3) + (sent_s * 0.3) + (fund_s * 0.1) + (sector_s * 0.1)
            
            # Collect Stats
            all_vcp_scores.append(vcp_s)
            all_supply_scores.append(supply_s)
            all_fund_scores.append(fund_s)
            all_sentiment_raw.append(raw_sent)
            all_sentiment_scores.append(sent_s)
            all_total_scores.append(total)

    # Analyze Results
    print("\n" + "="*50)
    print("ANALYSIS RESULTS (Jan 02 - Feb 10)")
    print("="*50)
    print(f"Total Samples: {len(all_total_scores)}")
    
    if not all_total_scores:
        print("No data found.")
        return

    # Helper to print stats
    def print_stats(name, data):
        data = np.array(data)
        print(f"\n[{name}]")
        print(f"  Mean:   {np.mean(data):.2f}")
        print(f"  Median: {np.median(data):.2f}")
        print(f"  Min:    {np.min(data):.2f}")
        print(f"  Max:    {np.max(data):.2f}")
        print(f"  StdDev: {np.std(data):.2f}")
        print(f"  > 80:   {np.sum(data >= 80)} ({np.sum(data >= 80)/len(data)*100:.1f}%)")
        print(f"  < 40:   {np.sum(data < 40)} ({np.sum(data < 40)/len(data)*100:.1f}%)")

    print_stats("TOTAL SCORE", all_total_scores)
    print_stats("VCP Score (20%)", all_vcp_scores)
    print_stats("Supply Score (30%)", all_supply_scores)
    print_stats("Sentiment Score (30%)", all_sentiment_scores)
    print_stats("Fundamental Score (10%)", all_fund_scores)
    
    print("\n[Raw Sentiment (-1.0 to 1.0)]")
    print(f"  Mean: {np.mean(all_sentiment_raw):.3f}") # Closer to 0 means Neutral
    
analyze_scores('20260102', '20260210')
