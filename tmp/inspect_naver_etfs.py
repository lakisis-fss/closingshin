import requests
import json

url = "https://finance.naver.com/api/sise/etfItemList.nhn"
res = requests.get(url)
if res.status_code == 200:
    data = res.json()
    items = data['result']['etfItemList']
    
    # 🕵️ 명탐정 목표 가격들 (배포 버전 수치 기반)
    targets = {
        'BANK': 16625,
        'IT': 18990,
        'SECURITIES': 27908,
        'STEEL': 15050,
        'BATTERY': 16340, # 아까 BATTERY가 20075원이 나왔으므로 이것도 확인 필요
        'AUTO': 15580
    }
    
    print(f"Total ETFs in Naver: {len(items)}")
    for it in items:
        price = int(it['nowVal'])
        name = it['itemname']
        code = it['itemcode']
        
        # 목표 가격과 일치하는 녀석이 있는지 전수 조사
        for key, target_p in targets.items():
            if abs(price - target_p) < 10: # 거의 비슷한 놈이 있으면 보고
                print(f"🎯 Match found for {key}: {code} | {name} | Price: {price} (Target: {target_p})")
        
        # 키워드로도 하나 더 찾아보기
        if '은행' in name or '증권' in name or 'IT' in name or '철강' in name:
            print(f"  [Keyword] {code}: {name} ({price})")
else:
    print(f"Error fetching Naver: {res.status_code}")
