import requests
import json

def test_vcp_api():
    url = "http://localhost:3000/api/vcp/20260318"
    r = requests.get(url)
    if r.ok:
        data = r.json()
        if data:
            print(f"Total records: {len(data)}")
            # Find 대주전자재료 (078600)
            target = next((item for item in data if item.get('ticker') == '078600'), None)
            if target:
                print("Found 대주전자재료 Sample:")
                print(json.dumps(target, indent=2, ensure_ascii=False))
            else:
                print("대주전자재료 not found, showing first record:")
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
    else:
        print(f"API Failed: {r.status_code}")

if __name__ == "__main__":
    test_vcp_api()
