import argparse
import subprocess
import os
import sys
from datetime import datetime, timedelta
import pb_utils
import pandas as pd
import FinanceDataReader as fdr

# Windows Console Encoding Fix
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

def is_trading_day(date_str: str) -> bool:
    """주어진 날짜가 한국 주식시장 개장일인지 확인 (FDR 사용)"""
    try:
        # KOSPI 지수 데이터를 통해 개장일 여부 확인 (PyKRX 대체)
        # pb_date 형식 (YYYY-MM-DD)으로 변환
        dt = datetime.strptime(date_str, "%Y%m%d")
        pb_date = dt.strftime("%Y-%m-%d")
        
        # PB에 해당 날짜 데이터가 있는지 먼저 확인 (가장 정확한 개장일 지표)
        # 모든 종목이 아닌 KOSPI 시총 1위 삼성전자 등을 체크
        check_ticker = "005930" 
        pb_data = pb_utils.fetch_pb_ohlcv(check_ticker, start_date=pb_date, end_date=pb_date)
        if pb_data is not None and not pb_data.empty:
            return True

        # PB에 없으면 FDR로 체크
        df = fdr.DataReader('KS11', pb_date, pb_date)
        return not df.empty
    except Exception as e:
        print(f"[경고] 개장일 확인 실패 ({date_str}): {e}")
        # 주말인지만 체크하는 기본 로직으로 대체
        return datetime.strptime(date_str, "%Y%m%d").weekday() < 5

def check_data_exists(date_str: str, check_type: str) -> bool:
    """PB에서 데이터 존재 여부 확인"""
    dt = datetime.strptime(date_str, "%Y%m%d")
    pb_date = dt.strftime("%Y-%m-%d")
    
    if check_type == 'vcp':
        records = pb_utils.query_pb("vcp_reports", filter_str=f"date='{pb_date}'", limit=1)
        return len(records) > 0
    elif check_type == 'news':
        records = pb_utils.query_pb("news", filter_str=f"date='{pb_date}'", limit=1)
        return len(records) > 0
    elif check_type == 'analysis':
        records = pb_utils.query_pb("news_analysis", filter_str=f"date='{pb_date}'", limit=1)
        return len(records) > 0
    return False

def run_script(script_name: str, date_str: str):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    print(f"\n[실행] {script_name} --date {date_str}")
    try:
        subprocess.run([sys.executable, script_path, "--date", date_str], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[오류] {script_name} 실행 실패: {e}")

def main():
    parser = argparse.ArgumentParser(description='News Collection & Analysis Pipeline (PB Integrated)')
    parser.add_argument('--start_date', type=str, help='Start date (YYYYMMDD)')
    parser.add_argument('--end_date', type=str, help='End date (YYYYMMDD)')
    parser.add_argument('--force', action='store_true', help='Force regeneration even if data exists')
    args = parser.parse_args()

    today_str = datetime.now().strftime("%Y%m%d")
    start_date = args.start_date if args.start_date else today_str
    end_date = args.end_date if args.end_date else start_date

    # 날짜 범위 생성
    start_dt = datetime.strptime(start_date, "%Y%m%d")
    end_dt = datetime.strptime(end_date, "%Y%m%d")
    current_dt = start_dt

    while current_dt <= end_dt:
        date_str = current_dt.strftime("%Y%m%d")
        print(f"\n{'='*50}")
        print(f"작업 대상 날짜: {date_str}")
        print(f"{'='*50}")

        # 1. 개장일 확인
        if not is_trading_day(date_str):
            print(f"[{date_str}] 휴장일입니다. 건너뜁니다.")
            current_dt += timedelta(days=1)
            continue

        # 2. VCP 리포트 존재 확인 (리포트가 있어야 종목 타겟팅 가능)
        if not check_data_exists(date_str, 'vcp'):
            print(f"[{date_str}] VCP 리포트가 없습니다. 02_scan_vcp.py를 먼저 실행하세요.")
            current_dt += timedelta(days=1)
            continue

        # 3. 뉴스 수집 (04_collect_news.py)
        if args.force or not check_data_exists(date_str, 'news'):
            run_script("04_collect_news.py", date_str)
        else:
            print(f"[{date_str}] 뉴스가 이미 수집되어 있습니다.")

        # 4. 뉴스 분석 (05_analyze_news.py)
        if args.force or not check_data_exists(date_str, 'analysis'):
            run_script("05_analyze_news.py", date_str)
        else:
            print(f"[{date_str}] 뉴스 분석이 이미 완료되어 있습니다.")

        current_dt += timedelta(days=1)

if __name__ == '__main__':
    main()
