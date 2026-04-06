import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import FinanceDataReader as fdr
import time
import warnings
import argparse
import subprocess
import re
import pb_utils
import requests
import json
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

# Windows Console Encoding Fix
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

warnings.filterwarnings('ignore')

# -----------------------------------------------------------------------------
# 설정
# -----------------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
RESULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
PROGRESS_FILE = os.path.join(DATA_DIR, "scan_progress.json")

# 대상 선정 설정
TARGET_WINNERS_COUNT = 100  # 시장별 선정 종목 수
LOOKBACK_DAYS = 50         # 상승률 계산 기간 (일)

# 스캔 제외 종목 패턴 (ETF/ETN/스팩/우선주/리츠)
EXCLUDE_NAME_PATTERNS = re.compile(
    r'(KODEX|TIGER|KBSTAR|KOSEF|HANARO|SOL|ACE|ARIRANG|BNK|'
    r'파워|인버스|레버리지|합성|ETN|스팩|리츠|부동산|인프라|'
    r'SPAC|선물|채권|단기|머니|Treasury|Bond)',
    re.IGNORECASE
)

# OHLCV 캐시 (Phase 1 -> Phase 2 재사용)
_ohlcv_cache: dict[str, pd.DataFrame] = {}

# VCP 파라미터
MIN_CONTRACTIONS = 2      # 최소 축소 횟수 (2T 이상)
MAX_DEPTH_1ST = 0.35      # 1차 조정 최대 깊이 (35% 이상 하락은 제외)
MIN_DEPTH_LAST = 0.02     # 마지막 조정 최소 깊이 (너무 작으면 노이즈)
MAX_DEPTH_LAST = 0.15     # 마지막 조정 최대 깊이 (15% 완화)

def parse_args():
    parser = argparse.ArgumentParser(description='VCP Scanner - Mark Minervini Style (Integrated)')
    parser.add_argument('--date', type=str, default=None,
                        help='Target date in YYYYMMDD format (default: today)')
    parser.add_argument('--save-targets', action='store_true',
                        help='Save the selected target list to CSV (for debugging)')
    parser.add_argument('--mode', type=str, default='classic', choices=['classic', 'aggressive', 'earlybird', 'stable', 'relaxed', 'custom'],
                        help='VCP detection mode')
    parser.add_argument('--min_contractions', type=int, default=2, help='Custom mode: min contractions (default: 2)')
    parser.add_argument('--max_depth_1st', type=float, default=0.35, help='Custom mode: max 1st depth (default: 0.35)')
    parser.add_argument('--min_depth_last', type=float, default=0.02, help='Custom mode: min last depth (default: 0.02)')
    parser.add_argument('--max_depth_last', type=float, default=0.15, help='Custom mode: max last depth (default: 0.15)')
    parser.add_argument('--strict_trend', type=str, default='true', choices=['true', 'false'], help='Custom mode: strict trend requirement')
    parser.add_argument('--no-sync', action='store_true', help='Skip local data synchronization')
    return parser.parse_args()

def run_sync():
    """스캔 전 시장 데이터 동기화 엔진 실행"""
    sync_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "08_sync_market_data.py")
    if os.path.exists(sync_script):
        print(f"[{datetime.now()}] 자동 시장 데이터 동기화 체크 중...")
        try:
            subprocess.run([sys.executable, sync_script], check=True)
            print(f"[{datetime.now()}] 동기화 확인 완료.")
        except Exception as e:
            print(f"[{datetime.now()}] 동기화 중 오류 발생 (무시하고 스캔 진행): {e}")

# -----------------------------------------------------------------------------
# Global Config based on Args
# -----------------------------------------------------------------------------
args = parse_args()
TODAY = args.date if args.date else datetime.now().strftime("%Y%m%d")

# Apply Mode Parameters
vcp_mode_name = args.mode.capitalize()
strict_trend = True
vcp_convergence_multiplier = 1.2

if args.mode == 'classic':
    MIN_CONTRACTIONS = 2
    MAX_DEPTH_1ST = 0.35
    MIN_DEPTH_LAST = 0.02
    MAX_DEPTH_LAST = 0.15
    strict_trend = True
elif args.mode == 'aggressive':
    MIN_CONTRACTIONS = 2
    MAX_DEPTH_1ST = 0.60
    MIN_DEPTH_LAST = 0.02
    MAX_DEPTH_LAST = 0.25
    strict_trend = False
elif args.mode == 'earlybird':
    MIN_CONTRACTIONS = 1
    MAX_DEPTH_1ST = 0.30
    MIN_DEPTH_LAST = 0.02
    MAX_DEPTH_LAST = 0.15
    strict_trend = False
elif args.mode == 'stable':
    MIN_CONTRACTIONS = 2
    MAX_DEPTH_1ST = 0.20
    MIN_DEPTH_LAST = 0.01
    MAX_DEPTH_LAST = 0.05
    strict_trend = True
    TARGET_WINNERS_COUNT = 200
elif args.mode == 'relaxed':
    MIN_CONTRACTIONS = 2
    MAX_DEPTH_1ST = 0.40
    MIN_DEPTH_LAST = 0.02
    MAX_DEPTH_LAST = 0.20
    strict_trend = False
    vcp_convergence_multiplier = 1.5
elif args.mode == 'custom':
    MIN_CONTRACTIONS = args.min_contractions
    MAX_DEPTH_1ST = args.max_depth_1st
    MIN_DEPTH_LAST = args.min_depth_last
    MAX_DEPTH_LAST = args.max_depth_last
    strict_trend = args.strict_trend.lower() == 'true'
    vcp_convergence_multiplier = 1.5


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def update_progress(step, progress, total, message, status="running"):
    pb_utils.update_scan_progress(step, progress, total, message, status)

# -----------------------------------------------------------------------------
# 1. 대상 종목 선정 로직
# -----------------------------------------------------------------------------

def get_latest_business_day(target_date=None):
    return target_date if target_date else TODAY

def get_start_date(end_date_str, days_delta):
    end_date = datetime.strptime(end_date_str, "%Y%m%d")
    start_date = end_date - timedelta(days=days_delta)
    return start_date.strftime("%Y%m%d")

def _is_excluded_stock(name):
    return bool(EXCLUDE_NAME_PATTERNS.search(name))

def _fetch_ohlcv_for_target(ticker, name, market_name, start_date, end_date):
    try:
        df = pb_utils.fetch_pb_ohlcv(ticker, limit=70)
        if df.empty or len(df) < 5: return None
        
        s_dt, e_dt = pd.to_datetime(start_date), pd.to_datetime(end_date)
        # pb_utils.fetch_pb_ohlcv already sets DatetimeIndex and handles TZ
        # If index is not timezone-naive, make it naive for consistency
        if df.index.tz is not None: df.index = df.index.tz_localize(None)

        ohlcv = df.loc[s_dt:e_dt]
        if ohlcv.empty or len(ohlcv) < 5: return None

        first_close = float(ohlcv['close'].iloc[0])
        last_close = float(ohlcv['close'].iloc[-1])
        if first_close <= 0: return None

        change_rate = ((last_close - first_close) / first_close) * 100
        avg_volume = ohlcv['volume'].iloc[-20:].mean()

        return {
            'Ticker': ticker, 'Market': market_name, '종목명': name,
            '등락률': round(change_rate, 2), '시가': int(ohlcv['open'].iloc[0]),
            '종가': int(last_close), '거래량': int(avg_volume),
        }
    except Exception: return None

def _fetch_ohlcv_1y(ticker, start_date, end_date):
    try:
        df = pb_utils.fetch_pb_ohlcv(ticker, limit=400)
        if df.empty or len(df) < 50: return None
        if 'date' in df.columns: df = df.set_index('date')
        # date 컬럼을 이미 DatetimeIndex로 변환했는지 확인 (pb_utils.fetch_pb_ohlcv는 변환됨)
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        if df.index.tz is not None: df.index = df.index.tz_localize(None)
        return df
    except Exception as e:
        print(f"  [Error] [{ticker}] Phase 2 individual fetch fail: {e}")
        return None

def get_top_winners(target_date=None):
    print(f"[{datetime.now()}] 대상 종목 선별 작업 시작 (Batch 모드)...")
    update_progress(1, 0, 100, "전체 종목 리스트 수집 중...")
    ensure_dir(DATA_DIR)
    
    # 1. 사용 가능한 거래일 리스트 조회 (삼성전자 '005930' 기준으로 시장 영업일 파악)
    try:
        # 특정 종목 하나를 기준으로 최근 100거래일의 날짜 리스트를 가져옴
        recs = pb_utils.query_pb("ohlcv", filter_str='code="005930"', sort="-date", limit=100)
        all_dates = [r['date'].split(' ')[0] for r in recs]
        if len(all_dates) < 5:
            print("[오류] 데이터 부족으로 선별 불가")
            return pd.DataFrame()
        
        end_date = target_date if target_date else all_dates[0].replace("-", "")
        # LOOKBACK_DAYS(50) 근처의 실제 거래일 선택 (데이터가 있는 날로 자동 매칭)
        start_date_idx = min(LOOKBACK_DAYS, len(all_dates)-1)
        start_date = all_dates[start_date_idx].replace("-", "")
        
        print(f"  선정 기간: {start_date} ~ {end_date} (약 {start_date_idx}거래일 기준)")
    except Exception as e:
        print(f"[오류] 날짜 계산 실패: {e}")
        return pd.DataFrame()

    # 2. 전 종목 리스트 수집 및 스캔 제외 필터 적용
    market_tickers = pb_utils.get_market_tickers()
    if not market_tickers:
        pb_recs = pb_utils.query_pb("stock_infos", limit=5000)
        market_tickers = [{'Ticker': r.get('ticker') or r.get('code'), 'Name': r.get('name')} for r in pb_recs if r.get('ticker') or r.get('code')]

    protection_tickers = pb_utils.get_investor_protection_tickers()
    valid_tickers = {}
    for item in market_tickers:
        t = str(item['Ticker']).zfill(6)
        n = item['Name']
        
        # 1. 이름 기반 필터링 (ETF 등)
        if _is_excluded_stock(n): 
            continue
            
        # 2. 투자자보호 종목 필터링 (관리, 정지, 경보)
        if t in protection_tickers:
            continue
            
        valid_tickers[t] = n
    
    # 3. Batch Fetch (시작일과 종료일 데이터 대량 조회)
    def fetch_date_batch(dt_str):
        # YYYYMMDD -> YYYY-MM-DD
        fmt = f"{dt_str[:4]}-{dt_str[4:6]}-{dt_str[6:8]}"
        # Date 타입 필드는 ~ (contains) 연산자 대신 범위 조회를 사용해야 함
        # 밀리초(.000Z)를 포함해야 정확한 비교가 가능함 (lexicographical comparison 대비)
        filter_str = f'date >= "{fmt} 00:00:00.000Z" && date <= "{fmt} 23:59:59.999Z"'
        return pb_utils.query_pb("ohlcv", filter_str=filter_str, limit=5000)

    update_progress(1, 10, 100, f"시장 데이터 조회 중 ({end_date})...")
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_end = executor.submit(fetch_date_batch, end_date)
        future_start = executor.submit(fetch_date_batch, start_date)
        end_recs = future_end.result()
        start_recs = future_start.result()

    # 4. 데이터 매핑 및 등락률 계산
    update_progress(1, 50, 100, "상승 종목 계산 중...")
    end_prices = {r['code']: float(r['close']) for r in end_recs if r.get('code')}
    start_prices = {r['code']: float(r['close']) for r in start_recs if r.get('code')}
    
    results = []
    for ticker, name in valid_tickers.items():
        p_end = end_prices.get(ticker)
        p_start = start_prices.get(ticker)
        if p_end and p_start and p_start > 0:
            change = ((p_end - p_start) / p_start) * 100
            results.append({
                'Ticker': ticker, 'Market': 'Market', '종목명': name,
                '등락률': round(change, 2), '종가': int(p_end)
            })

    if not results:
        print("[경고] 비교 가능한 데이터가 없습니다.")
        return pd.DataFrame()

    market_df = pd.DataFrame(results)
    top_targets = market_df.sort_values(by='등락률', ascending=False).head(TARGET_WINNERS_COUNT * 2).copy()
    update_progress(1, 100, 100, f"대상 종목 선별 완료 (총 {len(top_targets)}개)")
    print(f"[{datetime.now()}] 대상 선별 완료. (Batch 모드로 26분 -> 수 초로 단축)")
    return top_targets

# -----------------------------------------------------------------------------
# 2. VCP 패턴 분석 로직
# -----------------------------------------------------------------------------

def check_trend(df):
    if len(df) < 200: return False, "데이터 부족 (200일 미만)"
    current_price = df['close'].iloc[-1]
    ma50 = df['ma50'].iloc[-1]
    ma150 = df['ma150'].iloc[-1]
    ma200 = df['ma200'].iloc[-1]
    
    if current_price < ma50 and strict_trend: return False, "50일선 아래"
    if strict_trend:
        if current_price < ma200: return False, "200일선 아래"
        if not (ma50 > ma150 > ma200): return False, "이평선 역배열 (50>150>200 미충족)"
    else:
        if current_price < ma150: return False, "150일선 아래"
    return True, "상승 추세"

def find_contractions(df):
    sub_df = df.iloc[-120:].copy()
    if len(sub_df) < 60: return [], 0, "데이터 부족", 0
    prices = sub_df['close'].values
    peaks = []
    for i in range(5, len(prices)-5):
        if prices[i] == max(prices[i-5:i+6]): peaks.append((i, prices[i]))
    
    if len(peaks) < 2: return [], 0.0, "파동 부족", 0

    valid_adjustments = []
    for k in range(len(peaks)-1):
        p1_idx, p1_val = peaks[k]
        p2_idx, p2_val = peaks[k+1]
        interval_prices = prices[p1_idx:p2_idx]
        if len(interval_prices) == 0: continue
        min_val = min(interval_prices)
        depth = (p1_val - min_val) / p1_val
        valid_adjustments.append(depth)

    last_peak_idx, last_peak_val = peaks[-1]
    last_close = prices[-1]
    pivot_point = float(last_peak_val)
    current_depth = (last_peak_val - min(prices[last_peak_idx:], default=last_close)) / last_peak_val
    valid_adjustments.append(current_depth)
    
    is_vcp = False
    if len(valid_adjustments) >= MIN_CONTRACTIONS:
        if len(valid_adjustments) > 1 and valid_adjustments[0] > MAX_DEPTH_1ST:
            return valid_adjustments, valid_adjustments[-1], "1차 조정폭 과다", pivot_point
        if MIN_DEPTH_LAST <= valid_adjustments[-1] <= MAX_DEPTH_LAST:
            if MIN_CONTRACTIONS == 1: is_vcp = True
            elif len(valid_adjustments) >= 2 and valid_adjustments[-1] <= (valid_adjustments[-2] * vcp_convergence_multiplier):
                is_vcp = True
    
    return valid_adjustments, valid_adjustments[-1], "VCP 후보" if is_vcp else "패턴 미완성", pivot_point

def calculate_vcp_score_polymorphic(mode, contractions_count, last_depth, vol_dry_up, vol_ratio):
    vol_score = 0
    if vol_dry_up: vol_score += 20
    if vol_ratio < 0.5: vol_score += 10
    last_depth_pct = last_depth * 100
    if mode == 'classic':
        tight_score = 40 if last_depth_pct <= 5 else (30 if last_depth_pct <= 10 else 10)
        count_score = 30 if 3 <= contractions_count <= 4 else (20 if contractions_count == 2 else 10)
    elif mode == 'aggressive':
        tight_score = 40 if last_depth_pct <= 10 else (30 if last_depth_pct <= 20 else 15)
        count_score = 30 if contractions_count >= 3 else 20
    elif mode == 'earlybird':
        tight_score = 40 if last_depth_pct <= 5 else (30 if last_depth_pct <= 10 else 20)
        count_score = 30 if contractions_count == 1 else (25 if contractions_count == 2 else 10)
    elif mode == 'stable':
        tight_score = 40 if last_depth_pct <= 3 else (20 if last_depth_pct <= 5 else 0)
        count_score = 30 if 2 <= contractions_count <= 3 else 20
    elif mode == 'relaxed':
        tight_score = 40 if last_depth_pct <= 8 else (30 if last_depth_pct <= 15 else 15)
        count_score = 30 if contractions_count >= 2 else 10
    elif mode == 'custom':
        target_max_depth = MAX_DEPTH_LAST * 100
        target_min_depth = MIN_DEPTH_LAST * 100
        tight_score = 40 if last_depth_pct <= target_min_depth + 2 else (30 if last_depth_pct <= target_max_depth * 0.5 else 15)
        count_score = 30 if contractions_count > MIN_CONTRACTIONS else (25 if contractions_count == MIN_CONTRACTIONS else 10)
    else:
        tight_score = 40 if last_depth_pct <= 5 else (30 if last_depth_pct <= 10 else 10)
        count_score = 30 if 3 <= contractions_count <= 4 else 20
    return tight_score + vol_score + count_score

def main():
    if not args.no_sync:
        update_progress(1, 0, 100, "전 종목 데이터 동기화 중(08_sync_market_data.py)...", "running")
        run_sync()

    print(f"[{datetime.now()}] VCP 통합 스캔 시작    # [0] 대상 선정 (Phase 1)")
    target_date = args.date if args.date else TODAY
    update_progress(1, 10, 100, "VCP 스캔 초기화 중...", "running")
    
    targets = get_top_winners(target_date=target_date)
    if targets.empty:
        print("[오류] 대상 종목을 선정하지 못했습니다.")
        update_progress(1, 100, 100, "대상 선정 실패", "error")
        return

    if args.save_targets:
        targets.to_csv(os.path.join(DATA_DIR, f"target_list_{TODAY}.csv"), index=False, encoding='utf-8-sig')

    ensure_dir(RESULT_DIR)
    results = []
    end_date = TODAY
    start_date = (datetime.strptime(end_date, "%Y%m%d") - timedelta(days=365)).strftime("%Y%m%d")
    total = len(targets)
    
    # 스캔 대상(200개)에 대한 상세 데이터(1년치) 사전 로딩 (Batch Optimize)
    uncached = [str(row['Ticker']).zfill(6) for _, row in targets.iterrows() if str(row['Ticker']).zfill(6) not in _ohlcv_cache]
    if uncached:
        total_uncached = len(uncached)
        update_progress(2, 0, total_uncached, "스캔용 상세 데이터(1년치) 로딩 중 (Batch)...")
        print(f"[{datetime.now()}] 스캔 대상 {total_uncached}개 상세 데이터 로딩 시작...")
        
        # 200개 종목을 10개씩 묶어서 배치 요청 (PocketBase 쿼리 길이 제한 고려)
        batch_size = 10
        for i in range(0, total_uncached, batch_size):
            batch_tickers = uncached[i:i + batch_size]
            # filter=code="005930" || code="000660" ...
            filter_parts = [f'code="{t}"' for t in batch_tickers]
            filter_str = " || ".join(filter_parts)
            
            try:
                # 10개 종목 x 300거래일 = 약 3000개 레코드 (안정권)
                recs = pb_utils.query_pb("ohlcv", filter_str=filter_str, limit=5000, sort="+date")
                
                # 가져온 데이터를 Ticker별로 분리하여 캐시에 저장
                batch_df = pd.DataFrame(recs)
                if not batch_df.empty:
                    # date 컬럼 미리 변환
                    if 'date' in batch_df.columns:
                        batch_df['date'] = pd.to_datetime(batch_df['date'])

                    for t in batch_tickers:
                        t_df = batch_df[batch_df['code'] == t].copy()
                        if not t_df.empty:
                            if 'date' in t_df.columns: t_df = t_df.set_index('date')
                            # tz 제거 전 DatetimeIndex 인지 확인
                            if isinstance(t_df.index, pd.DatetimeIndex) and t_df.index.tz is not None:
                                t_df.index = t_df.index.tz_localize(None)
                            _ohlcv_cache[t] = t_df
                
                progress_val = min(i + batch_size, total_uncached)
                msg = f"상세 데이터 로딩 중 ({progress_val}/{total_uncached})"
                # 터미널에 상세 진행 상황 출력
                print(f"  - [{progress_val}/{total_uncached}] {' '.join(batch_tickers)} 로딩 완료")
                update_progress(2, progress_val, total_uncached, msg)
            except Exception as e:
                print(f"  [경고] 배치 로딩 중 오류 (개별 시도 fallback): {e}")
                # 오류 발생 시 개별적으로 시도
                for t in batch_tickers:
                    msg = f"데이터 로딩 중 (Fallback): {t}"
                    print(f"    - {t} 개별 로딩 시도 중...")
                    _ohlcv_cache[t] = _fetch_ohlcv_1y(t, start_date, end_date)

        update_progress(2, total_uncached, total_uncached, "데이터 로딩 완료. 정밀 스캔 시작!")
        print(f"[{datetime.now()}] 상세 데이터 로딩 완료. (총 {len(_ohlcv_cache)}개 캐싱됨)")

    skip_stats = {"trend": 0, "vcp_pattern": 0, "error": 0, "success": 0}
    for current_idx, (_, row) in enumerate(targets.iterrows()):
        ticker = str(row['Ticker']).zfill(6)
        name, market, change_50d = row['종목명'], row['Market'], row['등락률']
        update_progress(2, current_idx + 1, total, f"스캔 중: {name} ({ticker})")
        try:
            df = _ohlcv_cache.get(ticker)
            if df is None: df = pb_utils.fetch_pb_ohlcv(ticker, start_date=start_date, end_date=target_date)
            if df is None or df.empty: continue

            # Slice data up to target_date (Crucial for historical scans)
            target_dt = pd.to_datetime(target_date)
            if df.index.max() > target_dt:
                df = df.loc[:target_dt]
            if df.empty: continue

            df['ma50'] = df['close'].rolling(window=50).mean()
            df['ma150'] = df['close'].rolling(window=150).mean()
            df['ma200'] = df['close'].rolling(window=200).mean()
            
            is_uptrend, trend_msg = check_trend(df)
            if not is_uptrend:
                print(f" [{current_idx+1}/{total}] {name}({ticker}): {trend_msg} (제외) | 50일등락: {change_50d}%")
                skip_stats["trend"] += 1
                continue
                
            contractions, last_depth, pattern_msg, pivot_point = find_contractions(df)
            if pattern_msg == "VCP 후보":
                vol_ma50, vol_recent = df['volume'].iloc[-50:].mean(), df['volume'].iloc[-5:].mean()
                vol_ratio = vol_recent / vol_ma50 if vol_ma50 > 0 else 1.0
                vol_dry_up = vol_ratio < 0.8
                current_close = df['close'].iloc[-1]
                pivot_dist = round(((pivot_point - current_close) / current_close) * 100, 2) if current_close > 0 else 0
                vcp_score = calculate_vcp_score_polymorphic(args.mode, len(contractions), last_depth, vol_dry_up, vol_ratio)
                jump_score = 0 # Future implementation: Price action strength
                
                # RS Calculation (Minervini style raw score)
                if len(df) >= 250:
                    c = df['close'].iloc[-1]
                    c63 = df['close'].iloc[-63]
                    c126 = df['close'].iloc[-126]
                    c189 = df['close'].iloc[-189]
                    c252 = df['close'].iloc[-250] if len(df) >= 250 else df['close'].iloc[0]
                    raw_rs = round((2 * (c/c63) + (c/c126) + (c/c189) + (c/c252)) * 20, 1)
                else:
                    raw_rs = 0
                
                # Consolidation Weeks (Weeks since 52-week high)
                df_year = df.tail(250)
                high_val = df_year['high'].max()
                # Find the index of the high value
                high_date = df_year[df_year['high'] == high_val].index[-1]
                last_date = df.index[-1]
                # If index is string, convert to datetime
                if isinstance(last_date, str):
                    days_diff = (pd.to_datetime(last_date) - pd.to_datetime(high_date)).days
                else:
                    days_diff = (last_date - high_date).days
                consolidation_weeks = round(days_diff / 7, 1)

                print(f" -> [★발견★] {name} ({market}): {len(contractions)}회 수축, 마지막 {last_depth*100:.1f}%, 점수 {vcp_score} (RS {raw_rs}), 피벗 {pivot_point:,.0f}")
                results.append({
                    'ticker': ticker, 'name': name, 'market': market, 'close': current_close,
                    'volume': int(df['volume'].iloc[-1]), 'change_pct': float(df['change'].iloc[-1]),
                    'contractions_count': len(contractions), 'contractions_history': str([round(c*100, 1) for c in contractions]),
                    'last_depth_pct': round(last_depth * 100, 2), 'volume_dry_up': vol_dry_up,
                    'vol_ratio': round(vol_ratio, 2), 'vcp_score': vcp_score, 'jump_score': jump_score,
                    'pivot_point': int(pivot_point), 'pivot_distance_pct': pivot_dist, 'note': 'VCP Detected', 'vcp_mode': args.mode,
                    'relative_strength': raw_rs, 'consolidation_weeks': consolidation_weeks
                })
                skip_stats["success"] += 1
            else:
                print(f" [{current_idx+1}/{total}] {name}({ticker}): {pattern_msg} (제외)")
                skip_stats["vcp_pattern"] += 1
        except Exception as e:
            print(f" [{current_idx+1}/{total}] {name}({ticker}): 에러 - {e}")
            skip_stats["error"] += 1

    print(f"\n{'='*60}\n VCP 스캔 요약: 발견 {skip_stats['success']}, 추세제외 {skip_stats['trend']}, 패턴제외 {skip_stats['vcp_pattern']}, 에러 {skip_stats['error']}\n{'='*60}")

    if results:
        res_df = pd.DataFrame(results).sort_values(by='vcp_score', ascending=False)
        pb_token = pb_utils.get_pb_token()
        fmt_date = f"{str(target_date)[:4]}-{str(target_date)[4:6]}-{str(target_date)[6:8]} 00:00:00.000Z"
        for _, r in res_df.iterrows():
            pb_data = {
                "date": fmt_date, "ticker": r['ticker'], "name": r['name'], "market": r['market'],
                "price": float(r['close']), "close": float(r['close']), "change_pct": float(r['change_pct']),
                "volume": int(r['volume']), "vcp_stage": 0, "contractions_count": int(r['contractions_count']),
                "contractions_history": json.loads(r['contractions_history'].replace("'", '"')),
                "volume_dry_up": bool(r['volume_dry_up']), "relative_strength": float(r.get('relative_strength', 0)), 
                "consolidation_weeks": float(r.get('consolidation_weeks', 0)),
                "pivot_point": float(r['pivot_point']), "pivot_distance_pct": float(r['pivot_distance_pct']),
                "last_depth_pct": float(r['last_depth_pct']), "vol_ratio": float(r['vol_ratio']),
                "vcp_score": float(r['vcp_score']), "jump_score": float(r['jump_score']),
                "vcp_mode": r['vcp_mode'], "note": r['note'], "is_target": True
            }
            pb_utils.upsert_to_pb("vcp_reports", pb_data, f'ticker="{r["ticker"]}" && date="{fmt_date}"', token=pb_token)
        print(f"[완료] {len(res_df)}개 PB 업로드 완료.")
        

        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            kwargs = {'creationflags': 0x08000000} if os.name == 'nt' else {}
            
            # Step 3: Stock Data & ROI 
            # (Note: 06_collect_stock_data already internally sends Step 1/2 messages occasionally, 
            # we'll let 07_calc_portfolio finalize Step 3)
            pipeline = [
                ("06_collect_stock_data.py", "상세 데이터 수집 중..."),
                ("07_calc_portfolio.py", "수익률 및 포트폴리오 계산 중..."),
                ("04_collect_news.py", "네이버 뉴스 수집 중..."),
                ("05_analyze_news.py", "AI 뉴스 감성 분석 중..."),
                ("03_visualize_vcp.py", "VCP 분석 차트 생성 중...")
            ]

            for s, desc in pipeline:
                print(f"[{datetime.now()}] {s} 실행 중: {desc}")
                cmd = [sys.executable, os.path.join(script_dir, s), "--date", target_date]
                subprocess.run(cmd, check=True, **kwargs)
            
            # 최종 완료 보고 (Step 6 -> Step 8/Done)
            update_progress(6, 100, 100, "전체 스캔 파이프라인 및 분석 완료", "completed")
        except Exception as e:
            print(f"[오류] 파이프라인 중단: {e}")
            update_progress(8, 0, 0, f"파이프라인 실패: {e}", "error")
    else:
        update_progress(1, 100, 100, "발견된 종목 없음", "completed")

if __name__ == "__main__":
    main()
