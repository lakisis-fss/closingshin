import os
import json
import time
import random
import urllib.request
import urllib.parse
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
]

KST = timezone(timedelta(hours=9))

def get_news_api(query, display=100, start=1):
    if not CLIENT_ID or not CLIENT_SECRET: return None
    encText = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/news?query={encText}&display={display}&start={start}&sort=date"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
    try:
        response = urllib.request.urlopen(request)
        if response.getcode() == 200:
            return json.loads(response.read().decode('utf-8'))
    except: pass
    return None

def get_news_web_scraping(query, target_date_str, max_items=20):
    """
    Stabilized Hybrid Scraper for Naver Search 'Fender UI'
    """
    print(f"\n[Scraper] 🔄 Scrambling for {query} on {target_date_str}...")
    
    date_dot = target_date_str
    date_raw = date_dot.replace(".", "")
    query_enc = urllib.parse.quote(query)
    
    # Precise date filter URL
    url = f"https://search.naver.com/search.naver?where=news&query={query_enc}&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds={date_dot}&de={date_dot}&nso=so%3Ar%2Cp%3Afrom{date_raw}to{date_raw}%2Ca%3Aall"
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.naver.com/"
    }
    
    try:
        time.sleep(random.uniform(2.5, 4.0))
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[Scraper] HTTP {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Fender UI Selectors (Data Attributes are most stable)
        # 1. Try titles via heatmap target
        titles = soup.select('a[data-heatmap-target=".tit"]')
        # 2. Try bodies via heatmap target
        bodies = soup.select('a[data-heatmap-target=".body"]')
        # 3. Try sources via profile text
        sources = soup.select('.sds-comps-profile-info-title-text')
        
        # If no heatmap targets, fallback to class patterns (dynamic classes usually have stable prefixes or children)
        if not titles:
            print("[Scraper] No heatmap targets found. Falling back to generic patterns...")
            # Titles are often high-level headlines
            titles = soup.select('.sds-comps-text-type-headline1')
        
        results = []
        # Match them if possible, or just gather what we can
        for i, t_el in enumerate(titles):
            if i >= max_items: break
            
            title = t_el.get_text(strip=True)
            link = t_el.get('href', '')
            
            if not title or not link or link.startswith('#'): continue
            
            # Match body and source by index if possible
            desc = ""
            if i < len(bodies):
                desc = bodies[i].get_text(strip=True)
            
            source = "Naver News"
            if i < len(sources):
                source = sources[i].get_text(strip=True)
            
            results.append({
                'title': title,
                'link': link,
                'description': desc,
                'pubDate': f"{target_date_str} (Scraped)",
                'source': f"Scraping ({source})"
            })
            
        print(f"[Scraper] ✅ Collected {len(results)} items.")
        return results
        
    except Exception as e:
        print(f"[Scraper] Error: {e}")
        return []

def run_hybrid_debug(stock_name, target_date_str):
    target_dt_obj = datetime.strptime(target_date_str, "%Y.%m.%d").replace(tzinfo=KST)
    target_start = target_dt_obj.replace(hour=0, minute=0, second=0)
    target_end = target_dt_obj.replace(hour=23, minute=59, second=59)
    
    print(f"=== Hybrid System Debug: {stock_name} / {target_date_str} ===")
    
    api_results = []
    api_limit_reached = False
    last_api_date = None
    
    # 1. API Stage
    print("[1/2] API Collection Start...")
    for start_idx in range(1, 1001, 100):
        data = get_news_api(stock_name, display=100, start=start_idx)
        if not data or 'items' not in data or not data['items']:
            break
        items = data['items']
        api_results.extend(items)
        last_item_str = items[-1]['pubDate']
        try:
            last_date = datetime.strptime(last_item_str, '%a, %d %b %Y %H:%M:%S +0900').replace(tzinfo=KST)
            last_api_date = last_date
            if last_date < target_start: break
        except: pass
        if start_idx == 901: api_limit_reached = True
        time.sleep(0.1)
    
    valid_api_items = []
    for item in api_results:
        try:
            pub_date = datetime.strptime(item['pubDate'], '%a, %d %b %Y %H:%M:%S +0900').replace(tzinfo=KST)
            if target_start <= pub_date <= target_end:
                valid_api_items.append(item)
        except: continue
            
    print(f"[API] Found {len(valid_api_items)} items. LimitReached: {api_limit_reached}")

    # 2. Scraper Hybrid Logic
    final_data = valid_api_items
    
    # Trigger conditions
    if api_limit_reached and (not last_api_date or last_api_date > target_end):
        print(">> TRIGGER: NEWS VOLUME EXCEEDS API LIMIT (1000 items/1.5 days reach).")
        scraped = get_news_web_scraping(stock_name, target_date_str)
        final_data.extend(scraped)
    elif len(valid_api_items) == 0:
        print(">> TRIGGER: NO NEWS FOUND IN API. TRYING WEB SCRAPER...")
        scraped = get_news_web_scraping(stock_name, target_date_str)
        final_data.extend(scraped)
        
    print(f"\n--- MISSION COMPLETE: {len(final_data)} ITEMS TOTAL ---")
    for i, item in enumerate(final_data[:10]):
        src = item.get('source', 'Naver API')
        print(f"[{i+1}] {item['title'][:60]}... ({src})")

if __name__ == "__main__":
    run_hybrid_debug("한화에어로스페이스", "2026.03.11")
