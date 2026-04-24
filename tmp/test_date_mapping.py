import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils
from datetime import datetime

def simulate_frontend_logic():
    print("--- Simulating Frontend getAvailableVcpDates Logic ---")
    
    # 1. DB에서 모든 날짜 필드 가져오기
    recs = pb_utils.query_pb('vcp_reports', limit=5000, fields='date')
    print(f"Total records fetched: {len(recs)}")
    
    # 2. 날짜 변환 시뮬레이션
    # 프론트엔드: new Date(item.date) -> getFullYear, getMonth+1, getDate
    date_strings = []
    for r in recs:
        raw_date = r.get('date')
        if not raw_date: continue
        
        # UTC 자정 기준 문자열로 파싱
        try:
            # PB 날짜 형식: "2026-04-15 00:00:00.000Z"
            dt_utc = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S.%fZ")
            
            # Case A: 로컬 시간(KST +9)으로 해석할 경우
            # (dt_utc는 이미 UTC 기준이므로, 로컬 환경이 KST라면 9시간이 더해짐)
            # 여기서는 단순 문자열 기반 매핑 확인
            fmt = dt_utc.strftime("%Y%m%d")
            date_strings.append(fmt)
        except Exception as e:
            # 밀리초가 없는 경우 등 예외 처리
            print(f"Parse error for {raw_date}: {e}")

    unique_dates = sorted(list(set(date_strings)), reverse=True)
    print(f"\nUnique dates found ({len(unique_dates)}):")
    for d in unique_dates:
        # 15, 16일 강조
        mark = " <--- FOUND!" if d in ['20260415', '20260416'] else ""
        print(f"  - {d}{mark}")

if __name__ == "__main__":
    simulate_frontend_logic()
