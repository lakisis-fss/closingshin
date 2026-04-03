import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_naver_index_history(code, pages=3):
    history = {}
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for page in range(1, pages + 1):
        url = f"https://finance.naver.com/sise/sise_index_day.naver?code={code}&page={page}"
        res = requests.get(url, headers=headers)
        res.encoding = 'cp949'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        table = soup.select_one("table.type_1")
        if not table: continue
            
        rows = table.find_all("tr")
        for row in rows:
            date_el = row.select_one("td.date")
            number_els = row.select("td.number_1") # First one is the closing price
            
            if date_el and number_els:
                date_str = date_el.get_text(strip=True)
                price_str = number_els[0].get_text(strip=True).replace(',', '')
                if date_str and price_str:
                    try:
                        clean_dt = datetime.strptime(date_str, "%Y.%m.%d")
                        clean_date = clean_dt.strftime("%Y-%m-%d")
                        history[clean_date] = float(price_str)
                    except: continue
    
    return history

def test_scrape_history():
    kospi_map = scrape_naver_index_history('KOSPI', pages=6)
    kosdaq_map = scrape_naver_index_history('KOSDAQ', pages=6)
    
    print(f"KOSPI: {len(kospi_map)} points")
    print(f"KOSDAQ: {len(kosdaq_map)} points")
    
    common_dates = sorted(list(set(kospi_map.keys()) & set(kosdaq_map.keys())))
    print(f"Common dates: {len(common_dates)}")
    
    final_history = []
    for dt in common_dates:
        final_history.append({
            'date': dt,
            'KOSPI': kospi_map[dt],
            'KOSDAQ': kosdaq_map[dt]
        })
    
    print(f"Final history length: {len(final_history)}")
    if final_history:
        print(f"Last point: {final_history[-1]}")

if __name__ == "__main__":
    test_scrape_history()
