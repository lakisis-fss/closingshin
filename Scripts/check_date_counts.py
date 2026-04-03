import pb_utils

def check_date_counts(date_str):
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    pb_date_full = f"{formatted_date} 00:00:00.000Z"
    
    vcp = len(pb_utils.query_pb("vcp_reports", filter_str=f'date="{pb_date_full}"'))
    news = len(pb_utils.query_pb("news_reports", filter_str=f'date="{pb_date_full}"'))
    analysis = len(pb_utils.query_pb("news_analysis", filter_str=f'date="{pb_date_full}"'))
    
    print(f"Date: {pb_date_full}")
    print(f"VCP Reports: {vcp}")
    print(f"News Reports: {news}")
    print(f"News Analysis: {analysis}")

if __name__ == "__main__":
    check_date_counts("20260327")
