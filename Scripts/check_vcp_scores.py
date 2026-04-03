import pb_utils

def check_vcp_scores(date_str):
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    pb_date_full = f"{formatted_date} 00:00:00.000Z"
    
    recs = pb_utils.query_pb("vcp_reports", filter_str=f'date="{pb_date_full}"', limit=10)
    for rec in recs:
        print(f"Ticker: {rec.get('ticker')}, Name: {rec.get('name')}, Score: {rec.get('vcp_score')}")

if __name__ == "__main__":
    check_vcp_scores("20260327")
