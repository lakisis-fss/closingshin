import requests
from bs4 import BeautifulSoup

def find_ticker_by_price(target_price, keywords):
    print(f"\nSearching for target price {target_price:,} with keywords {keywords}...")
    # 네이버 금융 ETF 페이지 크롤링
    url = "https://finance.naver.com/api/sise/etfItemList.nhn"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        items = data['result']['etfItemList']
        for item in items:
            name = item['itemname']
            price = item['nowVal']
            code = item['itemcode']
            
            # 가격이 10% 내외이고 키워드가 포함된 경우 출력
            if (target_price * 0.9 <= price <= target_price * 1.1) and any(kw in name for kw in keywords):
                print(f"  [MATCH?] {code} ({name}): {price:,}")

# 배포 버전의 타겟 가격들
find_ticker_by_price(16340, ['2차전지', '배터리', 'BATTERY'])
find_ticker_by_price(18990, ['IT', '소프트웨어', '정보기술'])
find_ticker_by_price(16625, ['은행', '금융', 'BANK'])
find_ticker_by_price(27908, ['증권', 'SECURITIES'])
