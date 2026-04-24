import requests
import os

def check_public_access():
    pb_url = os.getenv('PB_URL', 'http://127.0.0.1:8090')
    print(f"Testing public access to {pb_url}...")
    
    # 토큰 없이 vcp_reports 조회 (프론트엔드와 동일한 조건)
    # perPage를 크게 잡아서 몇 개까지 나오는지 확인
    url = f"{pb_url}/api/collections/vcp_reports/records?perPage=1000&fields=date"
    
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('items', [])
            total = data.get('totalItems')
            print(f"Publicly visible records: {len(items)} (Total in DB: {total})")
            
            # 날짜별로 몇 개씩 있는지 카운트
            date_counts = {}
            for item in items:
                d = item.get('date', 'unknown')[:10]
                date_counts[d] = date_counts.get(d, 0) + 1
            
            print("\nDate distribution in first 1000 records:")
            for d in sorted(date_counts.keys(), reverse=True):
                print(f"  - {d}: {date_counts[d]} records")
        else:
            print(f"Public access failed with status: {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_public_access()
