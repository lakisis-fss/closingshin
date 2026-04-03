import requests
import json

url = "https://finance.naver.com/api/sise/etfItemList.nhn"
res = requests.get(url)
if res.status_code == 200:
    data = res.json()
    items = data['result']['etfItemList']
    
    print(f"Total ETFs searchable: {len(items)}")
    
    # 배포 버전 목표 가격
    p_battery = 16340
    p_securities = 27908
    
    for it in items:
        price = int(it['nowVal'])
        name = it['itemname']
        code = it['itemcode']
        
        if abs(price - p_battery) < 20:
            print(f"🕵️ BATTERY CANDIDATE: {name} | CODE: {code} | PRICE: {price} (Goal: {p_battery})")
        
        if abs(price - p_securities) < 20:
            print(f"🕵️ SECURITIES CANDIDATE: {name} | CODE: {code} | PRICE: {price} (Goal: {p_securities})")
            
        # 키워드로도 하나 더 찾아보고
        if '2차전지산업' in name or '증권' in name or '중소형' in name:
            print(f"  [Keyword] Name: {name} | Code: {code} | Price: {price}")
else:
    print(f"Error: {res.status_code}")
