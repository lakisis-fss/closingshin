"""
Historical Data Generator
--------------------------
국내 주식시장 개장일에 대해 VCP 스캔 및 관련 데이터를 순차적으로 생성합니다.

Usage:
    python generate_historical_data.py --start 20260101 --end 20260110
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime, timedelta

try:
    import FinanceDataReader as fdr
    HAS_FDR = True
except ImportError:
    HAS_FDR = False

try:
    from pykrx import stock
    HAS_PYKRX = True
except ImportError:
    HAS_PYKRX = False


def is_trading_day(date_str: str) -> bool:
    """
    주어진 날짜가 한국 주식시장 개장일인지 확인합니다.
    [2026.02.27] KRX API 실패 시 FDR 또는 주말 체크로 대체
    """
    dt = datetime.strptime(date_str, "%Y%m%d")
    
    # 1차: 주말 체크 (빠른 필터링)
    if dt.weekday() >= 5:  # 토(5), 일(6)
        return False
    
    # 2차: FDR로 KOSPI 지수 확인
    if HAS_FDR:
        try:
            date_dash = dt.strftime("%Y-%m-%d")
            df = fdr.DataReader('KS11', date_dash, date_dash)
            return len(df) > 0
        except:
            pass
    
    # 3차: pykrx KRX API 시도
    if HAS_PYKRX:
        try:
            df = stock.get_index_ohlcv_by_date(date_str, date_str, "1001")
            return len(df) > 0
        except:
            pass
    
    # 4차: 주말이 아니면 개장일로 간주 (공휴일은 놓칠 수 있음)
    print(f"  [Warning] Could not verify trading day for {date_str}, assuming open (weekday)")
    return True


def parse_args():
    parser = argparse.ArgumentParser(description='Historical Data Generator for Korean Stock Market')
    parser.add_argument('--start', type=str, required=True,
                        help='Start date in YYYYMMDD format')
    parser.add_argument('--end', type=str, required=True,
                        help='End date in YYYYMMDD format')
    parser.add_argument('--skip-news', action='store_true',
                        help='Skip news collection and analysis (faster)')
    return parser.parse_args()


def run_script(script_name: str, date_str: str, scripts_dir: str) -> bool:
    """
    지정된 스크립트를 날짜 인자와 함께 실행합니다.
    """
    script_path = os.path.join(scripts_dir, script_name)
    
    if not os.path.exists(script_path):
        print(f"[Error] Script not found: {script_path}")
        return False
    
    cmd = ["python", script_path, "--date", date_str]
    print(f"  Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=scripts_dir)
        if result.returncode != 0:
            print(f"  [Error] {script_name} failed:")
            print(result.stderr[:500] if result.stderr else "No error output")
            return False
        return True
    except Exception as e:
        print(f"  [Error] Failed to run {script_name}: {e}")
        return False


def generate_data_for_date(date_str: str, scripts_dir: str, skip_news: bool = False) -> dict:
    """
    특정 날짜에 대해 모든 데이터 생성 스크립트를 순차적으로 실행합니다.
    """
    results = {
        'date': date_str,
        'vcp_scan': False,
        'news_collect': False,
        'news_analyze': False,
        'stock_data': False
    }
    
    print(f"\n{'='*60}")
    print(f"Processing: {date_str}")
    print(f"{'='*60}")
    
    # 1. VCP Scan
    print("\n[1/4] VCP Scan...")
    results['vcp_scan'] = run_script("02_scan_vcp.py", date_str, scripts_dir)
    
    if not results['vcp_scan']:
        print("  Skipping remaining steps due to VCP scan failure.")
        return results
    
    # 2. News Collection (optional)
    if not skip_news:
        print("\n[2/4] News Collection...")
        results['news_collect'] = run_script("04_collect_news.py", date_str, scripts_dir)
        
        # 3. News Analysis (optional)
        if results['news_collect']:
            print("\n[3/4] News Analysis...")
            results['news_analyze'] = run_script("05_analyze_news.py", date_str, scripts_dir)
        else:
            print("  Skipping news analysis due to collection failure.")
    else:
        print("\n[2/4] News Collection... SKIPPED")
        print("\n[3/4] News Analysis... SKIPPED")
        results['news_collect'] = True
        results['news_analyze'] = True
    
    # 4. Stock Data Collection
    print("\n[4/4] Stock Data Collection...")
    results['stock_data'] = run_script("06_collect_stock_data.py", date_str, scripts_dir)
    
    return results


def get_date_range(start_str: str, end_str: str) -> list:
    """
    시작일부터 종료일까지의 날짜 목록을 생성합니다.
    """
    start = datetime.strptime(start_str, "%Y%m%d")
    end = datetime.strptime(end_str, "%Y%m%d")
    
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y%m%d"))
        current += timedelta(days=1)
    
    return dates


def main():
    args = parse_args()
    
    # Scripts 디렉토리 경로 확인
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("Historical Data Generator")
    print("=" * 60)
    print(f"Date Range: {args.start} ~ {args.end}")
    print(f"Scripts Dir: {scripts_dir}")
    print(f"Skip News: {args.skip_news}")
    
    # 날짜 범위 생성
    all_dates = get_date_range(args.start, args.end)
    print(f"Total Days: {len(all_dates)}")
    
    # 개장일만 필터링
    print("\nChecking trading days...")
    trading_days = []
    for d in all_dates:
        if is_trading_day(d):
            trading_days.append(d)
            print(f"  {d}: Trading Day")
        else:
            print(f"  {d}: Non-Trading Day (Holiday/Weekend)")
    
    print(f"\nTrading Days Found: {len(trading_days)}")
    
    if not trading_days:
        print("No trading days in the specified range. Exiting.")
        return
    
    # 데이터 생성 실행
    all_results = []
    for i, date_str in enumerate(trading_days):
        print(f"\n[{i+1}/{len(trading_days)}] Processing {date_str}...")
        result = generate_data_for_date(date_str, scripts_dir, args.skip_news)
        all_results.append(result)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'Date':<12} {'VCP':<8} {'News':<8} {'Analyze':<8} {'StockData':<10}")
    print("-" * 60)
    
    success_count = 0
    for r in all_results:
        vcp = "OK" if r['vcp_scan'] else "FAIL"
        news = "OK" if r['news_collect'] else "FAIL"
        analyze = "OK" if r['news_analyze'] else "FAIL"
        stock = "OK" if r['stock_data'] else "FAIL"
        
        print(f"{r['date']:<12} {vcp:<8} {news:<8} {analyze:<8} {stock:<10}")
        
        if r['vcp_scan'] and r['stock_data']:
            success_count += 1
    
    print("-" * 60)
    print(f"Successfully processed: {success_count}/{len(trading_days)} days")
    print("Done!")


if __name__ == "__main__":
    main()
