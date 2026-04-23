import os
import sys
import pandas as pd
import FinanceDataReader as fdr
import requests as req
import io
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import pb_utils
import json
import re
import argparse

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "prices")
os.makedirs(DATA_DIR, exist_ok=True)

# 한국 시간 기준 설정
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 40

def is_market_closed():
    now = datetime.now()
    if now.hour > MARKET_CLOSE_HOUR or (now.hour == MARKET_CLOSE_HOUR and now.minute >= MARKET_CLOSE_MINUTE):
        return True
    return False

# 스캔 제외 종목 패턴 (ETF/ETN/스팩/우선주/리츠 등 VCP 분석에 부적합한 종목)
EXCLUDE_NAME_PATTERNS = re.compile(
    r'(KODEX|TIGER|KBSTAR|KOSEF|HANARO|SOL|ACE|ARIRANG|BNK|'
    r'파워|인버스|레버리지|합성|ETN|스팩|리츠|부동산|인프라|'
    r'SPAC|선물|채권|단기|머니|Treasury|Bond)',
    re.IGNORECASE
)

def update_progress(step, progress, total, message, status="running"):
    pb_utils.update_scan_progress(step, progress, total, message, status)

# 전역 세션 생성 (커넥션 재사용으로 속도 향상)
session = req.Session()
adapter = req.adapters.HTTPAdapter(pool_connections=50, pool_maxsize=50)
session.mount('https://', adapter)
session.mount('http://', adapter)

def fast_fetch_ohlcv(ticker, count=100):
    """네이버 금융 차트 데이터 API를 직접 호출하거나 fdr.DataReader를 사용하여 OHLCV를 가져옵니다."""
    # 1. 네이버 금융 차트 API (빠른 속도)
    url = f"https://fchart.naver.com/sise.nhn?symbol={ticker}&timeframe=day&count={count}&requestType=0"
    try:
        resp = session.get(url, timeout=3)
        if resp.status_code == 200:
            data_match = re.search(r'\[\[.*\]\]', resp.text, re.DOTALL)
            if data_match:
                json_str = data_match.group(0).replace("'", '"')
                raw_data = json.loads(json_str)
                df_list = []
                for r in raw_data:
                    if len(r) < 6: continue
                    d = str(r[0])
                    df_list.append({
                        'Date': pd.to_datetime(f"{d[:4]}-{d[4:6]}-{d[6:8]}"),
                        'Open': float(r[1]), 'High': float(r[2]),
                        'Low': float(r[3]), 'Close': float(r[4]),
                        'Volume': int(r[5]), 'Change': 0.0
                    })
                df = pd.DataFrame(df_list)
                if not df.empty:
                    df['Change'] = df['Close'].pct_change()
                    return df
    except Exception:
        pass # Fallback to FinanceDataReader

    # 2. FinanceDataReader (안정적인 데이터 공급원)
    try:
        # 최근 N일치 데이터만 효율적으로 가져오기
        start_date = (datetime.now() - timedelta(days=count * 1.5)).strftime("%Y-%m-%d")
        df = fdr.DataReader(ticker, start=start_date)
        if not df.empty:
            df = df.reset_index()
            # fdr 컬럼명을 내부 규격(Date, Open, High, Low, Close, Volume, Change)으로 통일
            df = df.rename(columns={
                'Date': 'Date', 'Open': 'Open', 'High': 'High',
                'Low': 'Low', 'Close': 'Close', 'Volume': 'Volume', 'Change': 'Change'
            })
            # 타입 변환 및 정렬
            df['Date'] = pd.to_datetime(df['Date'])
            df['Change'] = df['Close'].pct_change()
            return df.tail(count)
    except Exception as e:
        print(f"  [Error] All fetch methods failed for {ticker}: {e}")
    return None

def sync_ticker_to_pb(ticker_info, token=None):
    ticker = ticker_info['Ticker']
    name = ticker_info['Name']
    
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    last_pb = pb_utils.query_pb("ohlcv", filter_str=f'code="{ticker}"', sort="-date", limit=1, token=token)
    
    # force 모드가 아니고 오늘 날짜 데이터가 이미 있으면 스킵
    force = getattr(args, 'force', False)
    
    count_needed = 10
    if last_pb:
        last_date = last_pb[0]['date'][:10]
        if last_date == today_str and not force:
            return f"[OK] {ticker} up-to-date."
        days_diff = (now - datetime.strptime(last_date, "%Y-%m-%d")).days
        count_needed = max(10, days_diff + 2)
    else:
        count_needed = 365 # 1년치

    try:
        df = fast_fetch_ohlcv(ticker, count=count_needed)
        if df is not None and not df.empty:
            count = 0
            df = df[df['Date'].dt.strftime("%Y-%m-%d") <= today_str]
            
            for _, row in df.sort_values('Date', ascending=False).iterrows():
                date_iso = row['Date'].strftime("%Y-%m-%d 00:00:00.000Z")
                date_only = row['Date'].strftime("%Y-%m-%d")
                
                if last_pb and date_only <= last_pb[0]['date'][:10]:
                    break
                
                payload = {
                    "code": ticker, "date": date_iso,
                    "open": float(row['Open']), "high": float(row['High']),
                    "low": float(row['Low']), "close": float(row['Close']),
                    "volume": int(row['Volume']), "change": float(row['Change'] if not pd.isna(row['Change']) else 0)
                }
                pb_utils.upsert_to_pb("ohlcv", payload, f'code="{ticker}" && date="{date_iso}"', token=token)
                count += 1
            return f"[UPDATED] {ticker} ({name}) +{count} rows"
    except Exception as e:
        return f"[ERROR] {ticker} ({name}): {e}"
    return None

def parse_args():
    parser = argparse.ArgumentParser(description='Market Data Sync Tool')
    parser.add_argument('--force', action='store_true', help='Force update even if today data exists')
    parser.add_argument('--ticker', type=str, help='Sync specific ticker only')
    return parser.parse_args()

args = parse_args()

def main():
    # 중복 실행 방지 (Lock)
    lock_file = os.path.join(DATA_DIR, "sync.lock")
    if os.path.exists(lock_file):
        # 30분 이상 된 락 파일은 무시 (프로세스 죽었을 경우 대비)
        if time.time() - os.path.getmtime(lock_file) < 1800:
            print(f"[{datetime.now()}] 다른 동기화 프로세스가 이미 실행 중입니다. (Lock)")
            return
    
    with open(lock_file, "w") as f: f.write(str(os.getpid()))
    
    try:
        print(f"[{datetime.now()}] PocketBase Market Data Sync Started (Optimized Batch Mode)...")
        update_progress(1, 0, 100, "시장 현황 확인 중...", "running")
        
        pb_token = pb_utils.get_pb_token()
        today_iso = datetime.now().strftime("%Y-%m-%d")
        
        # 1. 오늘 이미 동기화된 종목 리스트를 Batch로 한번에 가져와서 메모리에 캐싱
        print(f"[{datetime.now()}] 오늘 데이터 존재 여부 일괄 확인 중...")
        # Date 타입 필드는 ~ (contains) 연산자 대신 범위 조회를 사용해야 함
        # 밀리초(.000Z)를 포함해야 정확한 비교가 가능함
        filter_str = f'date >= "{today_iso} 00:00:00.000Z" && date <= "{today_iso} 23:59:59.999Z"'
        today_recs = pb_utils.query_pb("ohlcv", filter_str=filter_str, limit=5000, token=pb_token)
        synced_tickers = set([r['code'] for r in today_recs if r.get('code')])
        print(f"  -> 오늘 이미 동기화 완료된 종목: {len(synced_tickers)}개")
        
        # 2. 전체 종목 리스트 수집
        if args.ticker:
            tickers = [{'Ticker': args.ticker, 'Name': 'Specific Ticker'}]
        else:
            tickers = pb_utils.get_market_tickers()
            if not tickers:
                pb_recs = pb_utils.query_pb("stock_infos", limit=5000)
                tickers = [{'Ticker': r.get('ticker') or r.get('code'), 'Name': r.get('name')} for r in pb_recs if r.get('ticker') or r.get('code')]
        
        valid_tickers = [t for t in tickers if not EXCLUDE_NAME_PATTERNS.search(t['Name'])]
        
        # force 모드면 오늘 이미 동기화된 종목이라도 다시 수집 대상에 포함
        if args.force:
            to_sync_tickers = valid_tickers
        else:
            to_sync_tickers = [t for t in valid_tickers if t['Ticker'] not in synced_tickers]
        
        total_valid = len(valid_tickers)
        total_to_sync = len(to_sync_tickers)
        
        print(f"[{datetime.now()}] 대상 분석 완료: 총 {total_valid}개 중 {len(synced_tickers)}개 스킵, {total_to_sync}개 업데이트 필요")
        
        if total_to_sync == 0:
            print(f"[{datetime.now()}] 모든 종목이 이미 최신 상태입니다.")
            update_progress(1, 100, 100, "모든 데이터가 최신 상태입니다 (스킵 완료)", "running")
            return

        # 3. 업데이트 필요한 종목만 병렬 처리
        update_progress(1, 10, 100, f"데이터 업데이트 시작 ({total_to_sync}개 종목)...", "running")
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(sync_ticker_to_pb, t, pb_token): t for t in to_sync_tickers}
            for idx, future in enumerate(as_completed(futures)):
                current_num = idx + 1
                result = future.result()
                ticker_name = futures[future]['Name']
                
                # 로그 출력 주기 조절 (너무 잦으면 UI 노이즈)
                if current_num % 50 == 0 or current_num == total_to_sync:
                    print(f"[{current_num}/{total_to_sync}] {result if result else f'Syncing {ticker_name}...'}")
                    percent = 10 + (current_num / total_to_sync * 85)
                    msg = f"데이터 동기화 진행 중 ({current_num}/{total_to_sync}) - {ticker_name}"
                    update_progress(1, percent, 100, msg, "running")

        print(f"\n[{datetime.now()}] PB Market Data Sync Finished!")
        update_progress(1, 100, 100, "전 종목 데이터 동기화 완료!", "running")
    finally:
        if os.path.exists(lock_file):
            os.remove(lock_file)

if __name__ == "__main__":
    main()
