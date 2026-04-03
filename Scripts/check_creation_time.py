import pb_utils

def check_creation_time(date_str):
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    pb_date_full = f"{formatted_date} 00:00:00.000Z"
    
    recs = pb_utils.query_pb("news_analysis", filter_str=f'date="{pb_date_full}"', limit=5)
    for rec in recs:
        print(f"ID: {rec.get('id')}, Created: {rec.get('created')}")

if __name__ == "__main__":
    check_creation_time("20260327")
