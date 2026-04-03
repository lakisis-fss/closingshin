import os
import csv
import json
import time
import urllib.request
import urllib.parse
import difflib
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import argparse
import sys
import glob
import re
import pb_utils

# Windows Console Encoding Fix
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path=env_path)

CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
OUTPUT_FILE_PREFIX = "news_report_"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PROGRESS_FILE = os.path.join(DATA_DIR, "scan_progress.json")

# User-Agent list for safe scraping
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0 Safari/537.36"
]

def update_progress(step, progress, total, message, status="running"):
    pb_utils.update_scan_progress(step, progress, total, message, status)

def parse_args():
    parser = argparse.ArgumentParser(description='News Collector from VCP Report')
    parser.add_argument('--date', type=str, default=None,
                        help='Target date in YYYYMMDD format (default: latest)')
    return parser.parse_args()


def get_news_api(query, display=20, start=1):
    if not CLIENT_ID or not CLIENT_SECRET:
        return None

    encText = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/news?query={encText}&display={display}&start={start}&sort=date"
    
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
    
    try:
        response = urllib.request.urlopen(request)
        if response.getcode() == 200:
            return json.loads(response.read().decode('utf-8'))
    except:
        pass
    return None

def get_news_web_scraping(query, target_date_str, max_items=20):
    """
    Stabilized Scraper for Naver Search (Fender UI Support)
    target_date_str: YYYY.MM.DD
    """
    print(f"  [Scraper] 🔄 Starting web scraping for {query} ({target_date_str})...")
    
    date_dot = target_date_str
    date_raw = date_dot.replace(".", "")
    query_enc = urllib.parse.quote(query)
    
    url = f"https://search.naver.com/search.naver?where=news&query={query_enc}&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds={date_dot}&de={date_dot}&nso=so%3Ar%2Cp%3Afrom{date_raw}to{date_raw}%2Ca%3Aall"
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.naver.com/"
    }
    
    try:
        # Anti-bot delay
        time.sleep(random.uniform(2.0, 4.0))
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Fender UI Selectors (Stable Data-Heatmap-Target)
        titles = soup.select('a[data-heatmap-target=".tit"]')
        bodies = soup.select('a[data-heatmap-target=".body"]')
        sources = soup.select('.sds-comps-profile-info-title-text')
        
        # Fallback for old/different layout
        if not titles:
            titles = soup.select('a.news_tit') or soup.select('li.bx .news_contents a')
            bodies = soup.select('div.news_dsc')
            sources = soup.select('a.info.press')
        
        scraped_results = []
        for i, t_el in enumerate(titles):
            if i >= max_items: break
            
            title = t_el.get_text(strip=True)
            link = t_el.get('href', '')
            if not title or not link or link.startswith('#'): continue
            
            desc = bodies[i].get_text(strip=True) if i < len(bodies) else ""
            source_name = sources[i].get_text(strip=True) if i < len(sources) else "Naver"
            
            scraped_results.append({
                'title': title,
                'link': link,
                'description': desc,
                'pubDate': f"{target_date_str} (Scraped)",
                'originallink': link,
                'source_name': source_name
            })
            
        print(f"  [Scraper] Found {len(scraped_results)} items.")
        return scraped_results
    except Exception as e:
        print(f"  [Scraper Error] {e}")
        return []

def clean_html(text):
    text = text.replace("<b>", "").replace("</b>", "")
    text = text.replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return text

def is_similar(text1, text2, threshold=0.6):
    return difflib.SequenceMatcher(None, text1, text2).ratio() > threshold
def main():
    args = parse_args()
    date_str = args.date if args.date else datetime.now().strftime("%Y%m%d")
    
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    pb_date_full = f"{formatted_date} 00:00:00.000Z"
    
    KST = timezone(timedelta(hours=9))
    anchor_dt = datetime.strptime(date_str, "%Y%m%d").replace(hour=23, minute=59, second=59, tzinfo=KST)
    target_date_str_scrap = f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:8]}"
    
    print(f"Target Date (Anchor): {anchor_dt}")
    
    filter_str = f'date >= "{formatted_date} 00:00:00.000Z" && date <= "{formatted_date} 23:59:59.999Z"'
    rows = pb_utils.query_pb("vcp_reports", filter_str=filter_str, limit=100)
    if not rows:
        print(f"No VCP reports found in PB for {date_str}.")
        return

    results = []
    total = len(rows)
    for i, row in enumerate(rows):
        ticker = row.get('ticker')
        name = row.get('name')
        if not name: continue

        rank = i + 1
        if rank > 30: continue
        
        max_articles = 3 if rank <= 10 else 1
        update_progress(4, i+1, total, f"뉴스 데이터 수집 중... ({i+1}/{total})")
        
        all_items = []
        start_dt_limit = anchor_dt - timedelta(days=7)
        api_limit_reached = False
        last_api_date = None

        for start_idx in range(1, 1001, 100):
            news_data = get_news_api(name, display=100, start=start_idx)
            if not news_data or 'items' not in news_data or not news_data['items']:
                break
            
            items = news_data['items']
            all_items.extend(items)
            
            try:
                last_item_pub_date_str = items[-1]['pubDate']
                last_pub_date = datetime.strptime(last_item_pub_date_str, '%a, %d %b %Y %H:%M:%S +0900').replace(tzinfo=KST)
                last_api_date = last_pub_date
                if last_pub_date < start_dt_limit: break
            except: pass
            
            if start_idx == 901: api_limit_reached = True
            time.sleep(0.1)
        
        is_high_volume = api_limit_reached and (last_api_date and last_api_date > anchor_dt - timedelta(days=1))
        
        if is_high_volume or len(all_items) == 0:
            scraped_items = get_news_web_scraping(name, target_date_str_scrap, max_items=20)
            for s in scraped_items:
                all_items.append({
                    'title': s['title'], 'link': s['link'], 'description': s['description'],
                    'pubDate': s['pubDate'], 'originallink': s['link'], 'source_name': s['source_name']
                })

        results_for_ticker = []
        collected_titles = []
        for item in all_items:
            title = clean_html(item['title'])
            if any(is_similar(title, t) for t in collected_titles): continue
            
            pub_date_str = item['pubDate']
            try:
                if "(Scraped)" in pub_date_str:
                    pub_dt = anchor_dt
                else:
                    pub_dt = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S +0900').replace(tzinfo=KST)
                
                if pub_dt < start_dt_limit: continue
                
                score = 0
                lower_title = title.lower()
                if name.lower() in lower_title: score += 10
                if any(kw in lower_title for kw in ['공시', '실적', '계약', '수주', '상장', '특징주']): score += 5
                
                results_for_ticker.append({
                    'ticker': ticker, 'name': name, 'title': title, 'link': item['link'],
                    'description': clean_html(item.get('description', '')), 'pub_date': pub_dt, 'score': score
                })
                collected_titles.append(title)
            except: continue
        
        results_for_ticker.sort(key=lambda x: (x['score'], x['pub_date']), reverse=True)
        top_articles = results_for_ticker[:max_articles]
        results.extend(top_articles)
        print(f"  -> {name}: Found {len(results_for_ticker)} valid articles. Selected top {len(top_articles)}.")
        time.sleep(0.1)

    if results:
        try:
            pb_token = pb_utils.get_pb_token()
            print(f"[PB] Uploading {len(results)} news items to PocketBase...")
            for res in results:
                pb_data = {
                    "date": pb_date_full, "ticker": res['ticker'], "name": res['name'],
                    "title": res['title'], "link": res['link'], "description": res['description'],
                    "score": float(res['score'])
                }
                pb_utils.upsert_to_pb("news_reports", pb_data, f'link="{res["link"]}"', token=pb_token)
            print("[PB] Upload Done.")
        except Exception as e:
            print(f"[PB Error] Failed to upload news: {e}")
            
    print("Done.")

if __name__ == "__main__":
    main()
