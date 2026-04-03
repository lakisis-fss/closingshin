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

# User-Agent list for scraping
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
]

KST = timezone(timedelta(hours=9))

def get_news_web_scraping(query, target_date_str, max_items=20):
    print(f"\n[Scraper] 🔄 Fetching {query} on {target_date_str}...")
    
    date_dot = target_date_str
    date_raw = date_dot.replace(".", "")
    query_enc = urllib.parse.quote(query)
    
    # Updated URL with more params to mimic a real browser search
    url = f"https://search.naver.com/search.naver?where=news&query={query_enc}&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds={date_dot}&de={date_dot}&nso=so%3Ar%2Cp%3Afrom{date_raw}to{date_raw}%2Ca%3Aall"
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    try:
        time.sleep(random.uniform(2.0, 4.0))
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"[Scraper] Error: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Naver News items are usually in 'li.bx' or sometimes have specific data attributes
        # Let's try to find them by looking for news titles
        results = []
        
        # Pattern 1: Standard latest Naver News layout
        items = soup.select('li.bx')
        if not items:
            # Pattern 2: Maybe older or different layout
            items = soup.select('.news_area')
            
        print(f"[Scraper] Potentially found {len(items)} items. Parsing...")
        
        for idx, item in enumerate(items):
            if len(results) >= max_items:
                break
            
            # 1. Title
            title_el = item.select_one('a.news_tit') or item.select_one('a[class*="tit"]') or item.select_one('.api_txt_lines')
            if not title_el:
                continue
                
            title = title_el.get_text(strip=True)
            link = title_el.get('href', '')
            
            if not title or not link or link.startswith('#'):
                continue
            
            # 2. Source
            source_el = item.select_one('a.info.press') or item.select_one('.info_group a')
            source = source_el.get_text(strip=True) if source_el else "Unknown"
            
            # 3. Description
            desc_el = item.select_one('div.news_dsc') or item.select_one('.dsc_txt')
            desc = desc_el.get_text(strip=True) if desc_el else ""
            
            results.append({
                'title': title,
                'link': link,
                'description': desc,
                'pub_date': target_date_str,
                'source': f"Scraper ({source})"
            })
            
        if not results:
            print("[Scraper] DEBUG: No results found. Printing first 200 chars of HTML:")
            print(response.text[:200])
            
        return results
        
    except Exception as e:
        print(f"[Scraper] Exception: {e}")
        return []

if __name__ == "__main__":
    res = get_news_web_scraping("한화에어로스페이스", "2026.03.11")
    print(f"\nFinal Scraped Count: {len(res)}")
    for r in res[:5]:
        print(f"- {r['title']} ({r['source']})")
