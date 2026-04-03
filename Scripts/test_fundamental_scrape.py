import requests
from bs4 import BeautifulSoup

def test_scrape(ticker):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    url = f"https://finance.naver.com/item/main.naver?code={ticker}"
    res = requests.get(url, headers=headers, timeout=10)
    res.encoding = 'euc-kr'
    soup = BeautifulSoup(res.text, 'html.parser')

    def safe_float(selector):
        el = soup.select_one(selector)
        if el:
            print(f"Selector '{selector}': Found '{el.get_text()}'")
            try: 
                v = el.get_text().replace(',', '').replace('%', '').replace('배', '').strip()
                return float(v)
            except: return 0
        else:
            print(f"Selector '{selector}': NOT FOUND")
        return 0

    per = safe_float("#_per")
    pbr = safe_float("#_pbr")
    dvr = safe_float("#_dvr")
    
    print("\nChecking cop_analysis table...")
    rows = soup.select(".section.cop_analysis .tb_type1 tbody tr")
    print(f"Row count: {len(rows)}")
    for i, row in enumerate(rows):
        th = row.select_one("th")
        title = th.get_text(strip=True) if th else f"Row {i}"
        cols = row.select("td")
        vals = [c.get_text(strip=True) for c in cols]
        print(f"Line {i:2}: {title:20} -> {vals}")

if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "323280"
    test_scrape(ticker)
