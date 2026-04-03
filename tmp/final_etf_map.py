import requests
import json

url = "https://finance.naver.com/api/sise/etfItemList.nhn"
res = requests.get(url)
if res.status_code == 200:
    data = res.json()
    items = data['result']['etfItemList']
    
    # 배포 버전 목표들
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
    
    final_map = {}
    for key, target_p in targets.items():
        min_diff = 999999
        matched_code = ""
        matched_name = ""
        
        for it in items:
            p = int(it['nowVal'])
            diff = abs(p - target_p)
            if diff < min_diff:
                min_diff = diff
                matched_code = it['itemcode']
                matched_name = it['itemname']
        
        if min_diff < 100: # 100원 오차 범위 내에서 최고 근사치 선택
            final_map[key] = {
                "Code": matched_code,
                "Name": matched_name,
                "Price": target_p,
                "Current": matched_code # This is what we need
            }
            print(f"🎯 {key} Matched: {matched_name} ({matched_code}) | Diff: {min_diff}")
            
    print("\n--- FINAL TICKERS FOR SCRIPT ---")
    res_dict = {k: v['Code'] for k, v in final_map.items()}
    print(json.dumps(res_dict, indent=2))
else:
    print(f"Error: {res.status_code}")
