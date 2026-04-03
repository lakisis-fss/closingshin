import pb_utils
from datetime import datetime

def check_data(date_str):
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    pb_date_full = f"{formatted_date} 00:00:00.000Z"
    
    print(f"Checking data for {pb_date_full}")
    
    vcp_recs = pb_utils.query_pb("vcp_reports", filter_str=f'date="{pb_date_full}"', limit=100)
    print(f"VCP Reports: {len(vcp_recs)}")
    
    news_recs = pb_utils.query_pb("news_reports", filter_str=f'date="{pb_date_full}"', limit=100)
    print(f"News Reports: {len(news_recs)}")
    
    analysis_recs = pb_utils.query_pb("news_analysis", filter_str=f'date="{pb_date_full}"', limit=100)
    print(f"News Analysis: {len(analysis_recs)}")

if __name__ == "__main__":
    check_data("20260327")
