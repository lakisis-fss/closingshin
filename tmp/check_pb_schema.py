import sys
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_schema():
    pb_url = os.getenv('PB_URL', 'http://127.0.0.1:8090')
    print(f"Connecting to PocketBase at: {pb_url}")
    
    try:
        # 컬렉션 정보 조회
        resp = requests.get(f'{pb_url}/api/collections/vcp_reports')
        if resp.status_code == 200:
            coll = resp.json()
            print(f"Collection Name: {coll.get('name')}")
            print("Fields:")
            for field in coll.get('fields', []):
                print(f"  - {field.get('name')} ({field.get('type')})")
        else:
            print(f"Failed to fetch collection info: {resp.status_code}")
            
        # 전체 레코드 수 조회
        resp = requests.get(f'{pb_url}/api/collections/vcp_reports/records?perPage=1')
        if resp.status_code == 200:
            total = resp.json().get('totalItems')
            print(f"\nTotal Records in vcp_reports: {total}")
        else:
            print(f"Failed to fetch record count: {resp.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
