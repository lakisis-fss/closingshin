import pb_utils
from datetime import datetime
import pytz

# KST 시간대 설정
kst = pytz.timezone('Asia/Seoul')
now_kst = datetime.now(kst)
iso_date = now_kst.isoformat()[:10]

# 오늘 날짜로 생성된 모든 market_status 기록 검색
filter_str = f'date >= "{iso_date} 00:00:00" && date <= "{iso_date} 23:59:59"'
records = pb_utils.query_pb('market_status', filter=filter_str)

print(f"Found {len(records)} records for today ({iso_date}).")

# 모든 기록 삭제
for r in records:
    try:
        pb_utils.delete_pb('market_status', r['id'])
        print(f"  Deleted record ID: {r['id']}")
    except Exception as e:
        print(f"  Error deleting {r['id']}: {e}")

print("Wipe complete.")
