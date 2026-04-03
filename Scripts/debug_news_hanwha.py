import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

def get_news(query, display=100):
    encText = urllib.parse.quote(query)
    url = "https://openapi.naver.com/v1/search/news?query=" + encText + "&display=" + str(display) + "&sort=date"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
    try:
        response = urllib.request.urlopen(request)
        if response.getcode() == 200:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Exception: {e}")
    return None

KST = timezone(timedelta(hours=9))
# Anchor: 2026-03-11 23:59:59
anchor_dt = datetime(2026, 3, 11, 23, 59, 59, tzinfo=KST)
start_dt = anchor_dt - timedelta(days=7)

name = "한화에어로스페이스"
print(f"Analyzing {name} with anchor {anchor_dt}")
news_data = get_news(name)

if news_data and 'items' in news_data:
    items = news_data['items']
    print(f"Total items returned: {len(items)}")
    if items:
        print(f"First item date: {items[0]['pubDate']}")
        print(f"Last item date: {items[-1]['pubDate']}")
    
    count = 0
    for item in items:
        pub_date_str = item['pubDate']
        try:
            pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S +0900')
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=KST)
            
            if start_dt <= pub_date <= anchor_dt:
                count += 1
        except Exception as e:
            pass
    print(f"Total in range: {count}")
else:
    print("No news data returned")
