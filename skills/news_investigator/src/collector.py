import os
import csv
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import difflib
import json
import time

def clean_html(text):
    text = text.replace('<b>', '').replace('</b>', '')
    text = text.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return text

def is_similar(text1, text2, threshold=0.6):
    return difflib.SequenceMatcher(None, text1, text2).ratio() > threshold

def get_news(client_id, client_secret, query, display=20):
    encText = urllib.parse.quote(query)
    url = "https://openapi.naver.com/v1/search/news?query=" + encText + f"&display={display}&sort=date"
    
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    
    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if rescode == 200:
            response_body = response.read()
            return json.loads(response_body.decode('utf-8'))
        else:
            print(f"Error Code: {rescode}")
            return None
    except Exception as e:
        print(f"Error for query {query}: {e}")
        return None

def collect_news(target_file, client_id, client_secret):
    """
    Collects news for targets in the input CSV file.
    Returns a list of dictionaries containing news data.
    """
    if not os.path.exists(target_file):
        print(f"Target file not found: {target_file}")
        return []

    print(f"Reading target list from {target_file}...")
    targets = []
    with open(target_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            targets.append({'ticker': row['ticker'], 'name': row['name']})

    one_week_ago = datetime.now() - timedelta(days=7)
    results = []

    print(f"Fetching news for {len(targets)} targets...")

    for target in targets:
        ticker = target['ticker']
        name = target['name']
        print(f"Fetching news for {name} ({ticker})...")
        
        news_data = get_news(client_id, client_secret, name)
        
        if news_data:
            collected_titles = [] # Keep track of titles for this stock to check duplicates
            results_for_ticker = []

            for item in news_data['items']:
                try:
                    # Naver API date format: "Mon, 05 Feb 2026 15:30:00 +0900"
                    pub_date_str = item['pubDate']
                    pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S +0900')
                    
                    if pub_date > one_week_ago:
                        pub_date_str_iso = pub_date.strftime('%Y-%m-%d %H:%M')
                        title = clean_html(item['title'])
                        
                        # Check for duplicates using similarity
                        is_duplicate = False
                        for existing_title in collected_titles:
                            if is_similar(title, existing_title):
                                is_duplicate = True
                                break
                        
                        if is_duplicate:
                            continue

                        # Get score based on source
                        score = 0.7 # Default score (기타)
                        origin_link = item.get('originallink', '')
                        link = item.get('link', '')
                        
                        # Check original link first, then naver link
                        check_url = origin_link if origin_link else link
                        
                        if "hankyung.com" in check_url: score = 0.9 # 한국경제
                        elif "mk.co.kr" in check_url: score = 0.9 # 매일경제
                        elif "mt.co.kr" in check_url: score = 0.85 # 머니투데이
                        elif "sedaily.com" in check_url: score = 0.85 # 서울경제
                        elif "edaily.co.kr" in check_url: score = 0.85 # 이데일리
                        elif "yna.co.kr" in check_url: score = 0.85 # 연합뉴스
                        elif "news1.kr" in check_url: score = 0.8 # 뉴스1
                        
                        results_for_ticker.append({
                            'ticker': ticker,
                            'name': name,
                            'title': title,
                            'link': link,
                            'pub_date': pub_date_str_iso, # Sortable string
                            'description': clean_html(item['description']),
                            'score': score
                        })
                        collected_titles.append(title)
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    continue
            
            # Sort by score (desc), then date (desc)
            results_for_ticker.sort(key=lambda x: (x['score'], x['pub_date']), reverse=True)
            
            # Take top 3
            top_3 = results_for_ticker[:3]
            results.extend(top_3)
            
            print(f"  -> Found {len(results_for_ticker)} valid articles. Selected top {len(top_3)}.")
        
        # Be polite to the API
        time.sleep(0.1)
    
    return results
