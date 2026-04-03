import FinanceDataReader as fdr
from datetime import datetime, timedelta
import pytz

KST = pytz.timezone('Asia/Seoul')
now_kst = datetime.now(KST)
TODAY_DASH = now_kst.strftime("%Y-%m-%d")
start_dt = (now_kst - timedelta(days=7)).strftime("%Y-%m-%d")

print(f"Current KST Time: {now_kst}")
print(f"Fetching ^KS11 from {start_dt} to {TODAY_DASH}")

df = fdr.DataReader('^KS11', start_dt, TODAY_DASH)
print("\n--- KOSPI (^KS11) Data ---")
print(df.tail())

df_kosdaq = fdr.DataReader('^KQ11', start_dt, TODAY_DASH)
print("\n--- KOSDAQ (^KQ11) Data ---")
print(df_kosdaq.tail())

# Try crawling Naver for real-time price as well
import requests
from bs4 import BeautifulSoup

def get_naver_realtime(code):
    url = f"https://finance.naver.com/sise/sise_index.naver?code={code}"
    res = requests.get(url)
    res.encoding = 'cp949'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    now_value = soup.select_one("#now_value")
    if now_value:
        return float(now_value.text.replace(",", ""))
    return None

print("\n--- Naver Realtime Crawling ---")
print(f"KOSPI: {get_naver_realtime('KOSPI')}")
print(f"KOSDAQ: {get_naver_realtime('KOSDAQ')}")
