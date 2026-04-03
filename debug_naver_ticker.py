import requests
from bs4 import BeautifulSoup

def debug_naver_ticker(code):
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    res = requests.get(url, timeout=10)
    res.encoding = 'euc-kr'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    exday = soup.select_one(".no_exday")
    print(f"--- {code} ---")
    if exday:
        print(f"Exday text: {exday.text.strip()}")
        blind = exday.select_one(".blind")
        print(f"Blind text: {blind.text if blind else 'None'}")
        
debug_naver_ticker('069500') # KOSPI200
debug_naver_ticker('091160') # Semicon
