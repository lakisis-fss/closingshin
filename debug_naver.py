import requests
from bs4 import BeautifulSoup

def debug_naver_index(code):
    url = f"https://finance.naver.com/sise/sise_index.naver?code={code}"
    res = requests.get(url, timeout=10)
    res.encoding = 'cp949'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    cv_and_rate = soup.select_one("#change_value_and_rate")
    
    print(f"--- {code} ---")
    if cv_and_rate:
        # All nested tags
        for tag in cv_and_rate.descendants:
            if tag.name:
                print(f"  <{tag.name} class={tag.get('class')}> {tag.text.strip()} </{tag.name}>")
        
        # Check parent classes
        sise_info = soup.select_one(".sise_info")
        if sise_info:
            print(f"  Sise info classes: {sise_info.get('class', [])}")
            # Usually parent div has "up" or "down"
            # <div class="quot_kospi down">
        
        quot_div = soup.select_one(f".quot_{code.lower()}")
        if quot_div:
            print(f"  Quot div classes: {quot_div.get('class', [])}")

debug_naver_index('KOSPI')
debug_naver_index('KOSDAQ')
