import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from pocketbase import PocketBase
from pocketbase.utils import ClientResponseError
import FinanceDataReader as fdr
import requests
from bs4 import BeautifulSoup
import pytz

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path=env_path)

# PB Configuration
PB_URL = os.getenv("PB_URL", "http://localhost:8090")
PB_EMAIL = os.getenv("PB_EMAIL", "admin@example.com")
PB_PASSWORD = os.getenv("PB_PASSWORD", "admin1234")

# Global Client Instance
pb = PocketBase(PB_URL)

def get_pb_client():
    """PocketBase 클라이언트를 반환하며 필요한 경우 인증을 수행합니다."""
    if not pb.auth_store.token:
        try:
            pb.collection("_superusers").auth_with_password(PB_EMAIL, PB_PASSWORD)
        except Exception as e:
            print(f"[PB Error] Authentication failed: {e}")
    return pb

def normalize_pb_record(item):
    """PB 업로드 전 데이터 타입을 정규화하여 호환성 문제를 방지합니다."""
    if isinstance(item, list):
        return [normalize_pb_record(v) for v in item]
    elif isinstance(item, dict):
        clean_dict = {}
        for k, v in item.items():
            if k in ['ticker', 'code'] and v:
                clean_dict[k] = str(v).zfill(6)
            else:
                clean_dict[k] = normalize_pb_record(v)
        return clean_dict
    elif pd.isna(item) or item is None:
        return None
    elif isinstance(item, (np.integer, np.floating)):
        return item.item()
    elif isinstance(item, (datetime, pd.Timestamp)):
        if hasattr(item, 'tzinfo') and item.tzinfo:
            return item.isoformat()
        return item.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(item, (int, float, str, bool)):
        return item
    else:
        return str(item)

def query_pb(collection_name, filter_str=None, sort=None, limit=500, **kwargs):
    """컬렉션에서 데이터를 조회합니다."""
    client = get_pb_client()
    # Explicitly use token if provided for SDK calls if needed
    # (Though get_pb_client already handles stateful token, passing it explicitly ensures freshness)
    try:
        if limit > 500:
            # 대량 조회의 경우 get_full_list 사용
            items = client.collection(collection_name).get_full_list(
                query_params={
                    "filter": filter_str or "",
                    "sort": sort or ""
                }
            )
        else:
            result = client.collection(collection_name).get_list(
                page=1,
                per_page=limit,
                query_params={
                    "filter": filter_str or "",
                    "sort": sort or ""
                }
            )
            items = result.items

        records = []
        for item in items:
            # SDK 객체를 dict로 변환 (속성 직접 접근 활용)
            record_dict = {
                "id": item.id,
                "created": item.created,
                "updated": item.updated,
                "collectionId": item.collection_id,
                "collectionName": item.collection_name
            }
            
            # 추가 속성들 (field data)
            if hasattr(item, "__dict__"):
                record_dict.update(item.__dict__.copy())
            
            # extra_model_attrs가 있는 경우 (구버전 SDK 호환)
            if hasattr(item, "extra_model_attrs"):
                record_dict.update(item.extra_model_attrs)
            
            # id, created, updated 등 필드 중복 정리
            for k in ["collection_id", "collection_name"]:
                if k in record_dict: record_dict.pop(k)

            records.append(record_dict)
        return records
    except Exception as e:
        print(f"[PB Error] Query failed ({collection_name}): {e}")
        return []

def upload_to_pb(collection_name, data, method="post", record_id=None, **kwargs):
    """데이터를 생성하거나 업데이트합니다."""
    client = get_pb_client()
    record = normalize_pb_record(data)
    
    try:
        if method == "post":
            return client.collection(collection_name).create(record)
        elif method == "patch" and record_id:
            # PocketBase SDK v0.25+ 는 patch 대신 update 사용
            return client.collection(collection_name).update(record_id, record)
        return None
    except Exception as e:
        print(f"[PB Error] Upload failed ({collection_name}): {e}")
        return None

def insert_pb(collection_name, data, **kwargs):
    """데이터를 생성합니다 (upload_to_pb alias)."""
    return upload_to_pb(collection_name, data, method="post", **kwargs)

def update_pb(collection_name, record_id, data, **kwargs):
    """데이터를 수정합니다 (upload_to_pb alias)."""
    return upload_to_pb(collection_name, data, method="patch", record_id=record_id, **kwargs)

def upsert_to_pb(collection_name, data, filter_str, **kwargs):
    """기존 레코드가 있으면 수정하고, 없으면 생성합니다."""
    try:
        recs = query_pb(collection_name, filter_str=filter_str, **kwargs)
        if recs:
            return update_pb(collection_name, recs[0]['id'], data, **kwargs)
        return insert_pb(collection_name, data, **kwargs)
    except Exception:
        return insert_pb(collection_name, data, **kwargs)

def fetch_pb_ohlcv(ticker, start_date=None, end_date=None, limit=5000):
    """주가 데이터를 가져와서 Pandas DataFrame으로 반환합니다."""
    filter_expr = f'code="{str(ticker).zfill(6)}"'
    def normalize_date(d):
        d = str(d)
        if len(d) == 8 and d.isdigit():
            return f"{d[:4]}-{d[4:6]}-{d[6:8]}"
        return d

    if start_date:
        start_date = normalize_date(start_date)
        if " " not in start_date: start_date = f"{start_date} 00:00:00.000Z"
        filter_expr += f' && date >= "{start_date}"'
    if end_date:
        end_date = normalize_date(end_date)
        if " " not in end_date: end_date = f"{end_date} 23:59:59.999Z"
        filter_expr += f' && date <= "{end_date}"'
        
    try:
        # 이미 개선된 query_pb를 사용하여 레코드 가져오기
        recs = query_pb("ohlcv", filter_str=filter_expr, limit=limit, sort="-date")
        if not recs:
            return pd.DataFrame()
        
        df = pd.DataFrame(recs)
        # date 컬럼을 datetime으로 변환 후 정렬 및 인덱스 설정
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        return df
    except Exception as e:
        print(f"[PB Error] OHLCV Fetch failed ({ticker}): {e}")
        return pd.DataFrame()

def is_market_open():
    """한국 주식 시장 운영 시간(평일 09:00 ~ 15:30)인지 확인합니다."""
    try:
        KST = pytz.timezone('Asia/Seoul')
        now = datetime.now(KST)
        
        # 1. 주말 체크 (5: 토, 6: 일)
        if now.weekday() >= 5:
            return False
            
        # 2. 공휴일 체크 (보수적으로 2026년 주요 휴장일만 간단히 체크)
        today_str = now.strftime("%Y-%m-%d")
        HOLIDAYS = ['2026-01-01', '2026-02-16', '2026-02-17', '2026-02-18', '2026-03-02', 
                    '2026-05-05', '2026-05-25', '2026-08-17', '2026-09-24', '2026-09-25', 
                    '2026-09-26', '2026-09-28', '2026-10-05', '2026-10-09', '2026-12-25']
        if today_str in HOLIDAYS:
            return False
            
        # 3. 운영 시간 체크: 09:00 - 15:30 (데이터 수집 등을 위해 15:40까지 여유)
        current_time = now.hour * 100 + now.minute
        if 900 <= current_time <= 1540:
            return True
    except: pass
    return False

def get_realtime_price_naver(ticker):
    """네이버 폴링 API를 사용하여 실시간 현재가를 가져옵니다."""
    try:
        url = f"https://polling.finance.naver.com/api/realtime?query=SERVICE_ITEM:{ticker}"
        # 실시간 데이터이므로 짧은 타임아웃
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            data = res.json()
            if data.get('resultCode') == 'success':
                item = data['result']['areas'][0]['datas'][0]
                # nv 필드가 현재가
                if 'nv' in item and item['nv'] is not None:
                    return float(item['nv'])
    except: pass
    return None

def delete_pb(collection_name, record_id):
    """지정된 ID의 레코드를 삭제합니다."""
    client = get_pb_client()
    try:
        client.collection(collection_name).delete(record_id)
        return True
    except Exception as e:
        print(f"[PB Error] Delete failed ({collection_name}): {e}")
        return False

def get_synchronized_price(ticker):
    """지정된 티커의 가격을 조회합니다. 항상 네이버 실시간/종가 API를 최우선으로 합니다."""
    ticker = str(ticker).zfill(6)
    
    # [Priority 1] 장중/장마감 상관없이 네이버 API 호출 (가장 정확한 최근 종가/현재가)
    price = get_realtime_price_naver(ticker)
    if price:
        return price

    # [Priority 2] 실시간 API 실패 시 PB ohlcv 컬렉션 폴백
    client = get_pb_client()
    try:
        result = client.collection("ohlcv").get_list(
            page=1, per_page=1,
            query_params={"filter": f'code="{ticker}"', "sort": "-date"}
        )
        if result.items:
            return float(result.items[0].close)
    except: pass

    # [Priority 3] FinanceDataReader 최종 폴백 (종가 기준)
    try:
        import FinanceDataReader as fdr
        df = fdr.DataReader(ticker)
        if not df.empty:
            return float(df.iloc[-1]['Close'])
    except: pass

    return None

def get_pb_token():
    """인증 흐름을 확인하고 현재 토큰을 반환합니다."""
    client = get_pb_client()
    return client.auth_store.token

def get_market_tickers():
    """Naver Finance 시가총액 페이지를 크롤링하여 KOSPI, KOSDAQ 종목 리스트를 가져옵니다."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def fetch_page(sosok, page):
        url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}&page={page}"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code != 200: return []
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = soup.select('a.tltle')
            page_items = []
            for a in links:
                href = a.get('href', '')
                ticker = href.split('=')[-1]
                name = a.text.strip()
                if ticker and len(ticker) == 6:
                    page_items.append({'Ticker': ticker, 'Name': name})
            return page_items
        except: return []

    def get_last_page(sosok):
        url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}&page=1"
        try:
            resp = requests.get(url, timeout=5)
            soup = BeautifulSoup(resp.text, 'html.parser')
            pg_last = soup.select_one('td.pgRR a')
            if pg_last:
                href = pg_last.get('href', '')
                return int(href.split('=')[-1])
            return 10 # Fallback
        except: return 10

    print(f"[{datetime.now()}] Naver Finance에서 종목 리스트 수집 중...")
    results = []
    # sosok=0 (KOSPI), sosok=1 (KOSDAQ)
    for sosok in [0, 1]:
        last_page = get_last_page(sosok)
        print(f"  Market {sosok} has {last_page} pages.")
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_page, sosok, p) for p in range(1, last_page + 1)]
            for f in as_completed(futures):
                results.extend(f.result())

    # 중복 제거
    unique_pairs = []
    seen = set()
    for res in results:
        if res['Ticker'] not in seen:
            unique_pairs.append(res)
            seen.add(res['Ticker'])
            
    print(f"[PB Utils] Successfully fetched {len(unique_pairs)} tickers from Naver Finance.")
    
    # 만약 결과가 너무 적으면 stock_infos에서 가져오는 fallback
    if len(unique_pairs) < 500:
        print("[PB Utils] Naver result too small, checking stock_infos...")
        try:
            recs = query_pb("stock_infos", limit=5000)
            for r in recs:
                t = r.get('ticker') or r.get('code')
                n = r.get('name')
                if t and t not in seen:
                    unique_pairs.append({'Ticker': t, 'Name': n})
                    seen.add(t)
        except: pass
        
    return unique_pairs

def get_investor_protection_tickers():
    """
    네이버 금융에서 투자자보호 종목(관리종목, 거래정지, 시장경보)의 티커 목록을 가져옵니다.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    urls = [
        "https://finance.naver.com/sise/management.naver",
        "https://finance.naver.com/sise/trading_halt.naver",
        "https://finance.naver.com/sise/investment_alert.naver"
    ]
    
    def fetch_tickers(url):
        try:
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            if resp.status_code != 200: return set()
            soup = BeautifulSoup(resp.text, 'html.parser')
            tickers = set()
            for a in soup.select('a.tltle'):
                href = a.get('href', '')
                if 'code=' in href:
                    code = href.split('code=')[-1]
                    if len(code) == 6:
                        tickers.add(code)
            return tickers
        except: return set()
        
    excluded = set()
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(fetch_tickers, url) for url in urls]
        for f in as_completed(futures):
            excluded.update(f.result())
            
    print(f"[{datetime.now()}] 투자자보호 종목(관리/정지/경보) {len(excluded)}개 수집 완료.")
    return excluded


def update_scan_progress(step, progress, total, message, status="running"):
    """PocketBase의 settings 컬렉션에 스캔 진행률을 업데이트합니다."""
    try:
        data = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "progress": progress,
            "total": total,
            "percent": round((progress / total) * 100, 1) if total > 0 else 0,
            "message": message,
            "status": status
        }
        # settings 컬렉션에 key='scan_progress'로 통합 관리
        upsert_to_pb("settings", {"key": "scan_progress", "value": data}, 'key="scan_progress"')
    except Exception as e:
        print(f"[PB Error] Failed to update scan progress: {e}")

def log_to_pb(message, source="Python", level="INFO"):
    """PocketBase의 system_logs 컬렉션에 로그를 직접 기록합니다."""
    try:
        insert_pb("system_logs", {
            "message": str(message),
            "source": source,
            "level": level
        })
    except Exception as e:
        print(f"[PB Error] Logging failed: {e}")
