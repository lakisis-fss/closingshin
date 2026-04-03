import requests
from bs4 import BeautifulSoup
import re

def get_realtime_etf(ticker):
    """Naver Finance ETF real-time price"""
    url = f"https://finance.naver.com/item/main.naver?code={ticker}"
    res = requests.get(url)
    res.encoding = 'euc-kr' 
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Check if price exists
    price_tag = soup.select_one(".no_today .blind")
    if price_tag:
        price = int(price_tag.text.replace(",", ""))
        
        # Change Pct
        change_tag = soup.select_one(".no_exday .blind")
        if change_tag:
            # We need to find if it is UP or DOWN
            inner = soup.select_one(".no_exday")
            is_up = "상승" in inner.text or "상한" in inner.text
            is_down = "하락" in inner.text or "하한" in inner.text
            
            diff = int(change_tag.text.replace(",", ""))
            if is_down: diff *= -1
            
            prev_close = price - diff
            change_pct = (diff / prev_close) * 100
            return price, round(change_pct, 2)
    return None, None

def get_realtime_macro(code):
    """
    Naver Finance Macro indices
    FX_USDKRW, OIL_CL, OIL_DU, BONDS_US_10Y
    """
    url = f"https://finance.naver.com/marketindex/worldExchangeDetail.naver?marketindexCode={code}"
    # Wait, marketindex format is different.
    # FX: https://finance.naver.com/marketindex/exchangeDetail.naver?marketindexCode=FX_USDKRW
    # Oil: https://finance.naver.com/marketindex/worldOilDetail.naver?marketindexCode=OIL_CL&fdtc=2
    # Bond: https://finance.naver.com/marketindex/worldBondDetail.naver?marketindexCode=BONDS_US_10Y
    
    # Simplified naver scraping for indices
    pass

# Testing KOSPI200 ETF
price, pct = get_realtime_etf("069500")
print(f"KOSPI200 Live: {price} ({pct}%)")
