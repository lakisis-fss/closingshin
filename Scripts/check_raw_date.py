import pb_utils

def check_raw_date(date_str):
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    pb_date_full = f"{formatted_date} 00:00:00.000Z"
    
    # Try a broader search first
    recs = pb_utils.query_pb("news_analysis", filter_str=f'date ~ "{formatted_date}"', limit=5)
    for rec in recs:
        print(f"ID: {rec.get('id')}")
        print(f"Date (Raw): {rec.get('date')}")

if __name__ == "__main__":
    check_raw_date("20260327")
