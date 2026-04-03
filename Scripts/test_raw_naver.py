
import requests
from bs4 import BeautifulSoup

url = "https://finance.naver.com/sise/sise_index.naver?code=KOSPI"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    res = requests.get(url, headers=headers)
    res.encoding = 'cp949'
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        now_val = soup.select_one("#now_value")
        if now_val:
            print(f"Current KOSPI: {now_val.text}")
        else:
            print("Could not find #now_value")
            # print(res.text[:500])
except Exception as e:
    print(f"Raw Request Failed: {e}")
