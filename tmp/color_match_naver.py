import requests
import json

url = "https://finance.naver.com/api/sise/etfItemList.nhn"
res = requests.get(url)
if res.status_code == 200:
    data = res.json()
    items = data['result']['etfItemList']
    
    # 🕵️ 명탐정 목표 가격들 (배포 버전 수치 기반)
    # 현재가(nowVal)가 이 숫자들과 10원 내외로 일치하는 코드를 찾습니다.
    targets = {
        'KOSPI200': 86660,
        'SEMICON': 103865,
        'BATTERY': 16340,
        'AUTO': 15580,
        'IT': 18990,
        'BANK': 16625,
        'STEEL': 15050,
        'SECURITIES': 27908
    }
    
    print(f"Total ETFs searchable: {len(items)}")
    results = {}
    for it in items:
        price = int(it['nowVal'])
        code = it['itemcode']
        name = it['itemname']
        
        for key, target_p in targets.items():
            if abs(price - target_p) < 20: # 20원 오차 허용 (가격 변동성 고려)
                print(f"🎯 Match found for {key}: CODE={code} | NAME={name} | PRICE={price} (Target: {target_p})")
                results[key] = code

    print("\n--- RECOMMENDED TICKERS FOR 05_collect_market_status.py ---")
    print(json.dumps(results, indent=2))
else:
    print(f"Error: {res.status_code}")
