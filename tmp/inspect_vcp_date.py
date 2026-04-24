import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def inspect_date():
    target_date = '2026-04-15'
    print(f"--- Inspecting records for {target_date} ---")
    
    # 해당 날짜의 레코드 하나 가져오기
    records = pb_utils.query_pb('vcp_reports', filter_str=f'date~"{target_date}"', limit=1)
    
    if records:
        record = records[0]
        print(f"Record found! Ticker: {record.get('ticker')}")
        print(f"Raw Date field: '{record.get('date')}'")
        
        # 전체 날짜 리스트 확인 (프론트엔드 api.ts의 getAvailableVcpDates 로직 모사)
        all_records = pb_utils.query_pb('vcp_reports', limit=500, sort='-date')
        unique_dates = sorted(list(set([r.get('date') for r in all_records])), reverse=True)
        print("\nExisting unique dates in DB:")
        for d in unique_dates[:20]:
            print(f"  - {d}")
    else:
        print(f"No records found for {target_date} in vcp_reports.")

if __name__ == "__main__":
    inspect_date()
