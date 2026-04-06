import requests
from bs4 import BeautifulSoup

def get_naver_tickers(url):
    resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(resp.text, 'html.parser')
    tickers = []
    # 보통 a 태그의 href에 code=000000 형태로 있음
    for a in soup.select('a.tltle'):
        href = a.get('href', '')
        if 'code=' in href:
            code = href.split('code=')[-1]
            if len(code) == 6:
                tickers.append(code)
    return set(tickers)

if __name__ == '__main__':
    mgmt = get_naver_tickers("https://finance.naver.com/sise/management.naver")
    halt = get_naver_tickers("https://finance.naver.com/sise/trading_halt.naver")
    alert = get_naver_tickers("https://finance.naver.com/sise/investment_alert.naver")
    
    print(f"관리종목 수: {len(mgmt)}")
    print(list(mgmt)[:5])
    print(f"거래정지 수: {len(halt)}")
    print(list(halt)[:5])
    print(f"시장경보 수: {len(alert)}")
    print(list(alert)[:5])
