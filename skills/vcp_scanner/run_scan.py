
import os
import sys
import argparse
import pandas as pd
import io
from datetime import datetime, timedelta
from pykrx import stock
import requests
import time
import warnings

warnings.filterwarnings('ignore')

# -----------------------------------------------------------------------------
# 유틸리티 함수
# -----------------------------------------------------------------------------
def get_start_date(end_date_str, days_delta):
    end_date = datetime.strptime(end_date_str, "%Y%m%d")
    start_date = end_date - timedelta(days=days_delta)
    return start_date.strftime("%Y%m%d")

def check_trend(df):
    """추세 분석 (간소화)"""
    if len(df) < 200:
        return False
    current_price = df['종가'].iloc[-1]
    ma50 = df['종가'].rolling(window=50).mean().iloc[-1]
    ma150 = df['종가'].rolling(window=150).mean().iloc[-1]
    ma200 = df['종가'].rolling(window=200).mean().iloc[-1]
    
    # 200일선 위 & 정배열 경향
    if current_price < ma200:
        return False
    # 엄격한 정배열이 아니더라도 200일선 지지 중이면 OK
    return True

def find_contractions(df, min_cnt):
    """VCP 패턴 분석 (간소화)"""
    sub_df = df.iloc[-120:].copy()
    if len(sub_df) < 60: return [], 0
    
    prices = sub_df['종가'].values
    peaks = []
    # 고점 찾기
    for i in range(5, len(prices)-5):
        if prices[i] == max(prices[i-5:i+6]):
            peaks.append((i, prices[i]))
            
    if len(peaks) < 2: return [], 0
    
    # 조정폭 계산
    valid_adjustments = []
    for k in range(len(peaks)-1):
        p1_val = peaks[k][1]
        p2_idx = peaks[k+1][0]
        min_val = min(prices[peaks[k][0]:p2_idx])
        depth = (p1_val - min_val) / p1_val
        valid_adjustments.append(depth)
        
    # 마지막 고점 이후 현재까지
    last_peak_val = peaks[-1][1]
    last_idx = peaks[-1][0]
    current_min = min(prices[last_idx:])
    last_depth = (last_peak_val - current_min) / last_peak_val
    valid_adjustments.append(last_depth)
    
    if len(valid_adjustments) >= min_cnt:
        # 마지막 조정폭이 적절한지 (2~15%)
        if 0.02 <= valid_adjustments[-1] <= 0.15:
            # 줄어드는 경향
            if valid_adjustments[-1] < valid_adjustments[-2]:
                return valid_adjustments, valid_adjustments[-1]
                
    return [], 0

def get_tickers_from_kind(market_type):
    """
    [2026.02.27 KRX 로그인 필수 변경 대응]
    KRX KIND에서 종목 목록을 가져옵니다. (로그인 불필요)
    market_type: 'stockMkt' (KOSPI) or 'kosdaqMkt' (KOSDAQ)
    """
    kind_url = "https://kind.krx.co.kr/corpgeneral/corpList.do"
    resp = requests.get(
        kind_url, 
        params={'method': 'download', 'marketType': market_type},
        headers={'User-Agent': 'Mozilla/5.0'},
        timeout=15
    )
    if resp.status_code != 200:
        return [], []
    
    ticker_df = pd.read_html(io.StringIO(resp.text), encoding='euc-kr')[0]
    tickers = ticker_df['종목코드'].apply(lambda x: str(x).zfill(6)).tolist()
    names = ticker_df['회사명'].tolist()
    return tickers, names

# -----------------------------------------------------------------------------
# 메인 로직
# -----------------------------------------------------------------------------
def run_vcp_scan(lookback_days, top_n, min_contractions, output_file):
    """
    [2026.02.27 KRX 로그인 필수 변경 대응]
    - 종목 목록: KRX KIND (kind.krx.co.kr) - 로그인 불필요
    - OHLCV: pykrx Naver 백엔드 (adjusted=True) - 로그인 불필요
    - 등락률: OHLCV 데이터에서 직접 계산
    """
    print(f"[{datetime.now()}] VCP 스캔 시작 (기간:{lookback_days}일, 상위:{top_n}개, 축소:{min_contractions}회)")
    
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = get_start_date(end_date, lookback_days + 10)
    
    # 1. 대상 종목 선정 (KRX KIND + Naver OHLCV)
    markets_config = {
        "KOSPI": "stockMkt",
        "KOSDAQ": "kosdaqMkt"
    }
    targets = []
    
    for market_name, market_type in markets_config.items():
        print(f"[{market_name}] 종목 목록 수집 중...")
        tickers, names = get_tickers_from_kind(market_type)
        
        if not tickers:
            print(f"[{market_name}] 종목 목록 수집 실패")
            continue
        
        print(f"[{market_name}] {len(tickers)}개 종목 등락률 계산 중...")
        results = []
        
        for j, (ticker, name) in enumerate(zip(tickers, names)):
            try:
                ohlcv = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
                if ohlcv is None or ohlcv.empty or len(ohlcv) < 5:
                    continue
                first_close = ohlcv['종가'].iloc[0]
                last_close = ohlcv['종가'].iloc[-1]
                if first_close <= 0:
                    continue
                change_rate = ((last_close - first_close) / first_close) * 100
                results.append({
                    'Ticker': ticker,
                    'Market': market_name,
                    '종목명': name,
                    '등락률': round(change_rate, 2),
                })
            except:
                continue
            time.sleep(0.05)
            
            if (j + 1) % 100 == 0:
                print(f"  [{market_name}] {j+1}/{len(tickers)} 처리...")
        
        if results:
            market_df = pd.DataFrame(results)
            market_df = market_df.sort_values(by='등락률', ascending=False).head(top_n)
            targets.append(market_df)
            print(f"[{market_name}] 상위 {top_n}개 선정 완료.")
            
    if not targets:
        print("대상 종목이 없습니다.")
        return

    target_df = pd.concat(targets)
    print(f"총 {len(target_df)}개 후보 종목에 대해 VCP 분석 시작...")
    
    # 2. VCP 분석
    results = []
    scan_start = get_start_date(end_date, 365) # 1년치 데이터
    
    for i, row in target_df.iterrows():
        ticker = str(row['Ticker']).zfill(6)
        name = row['종목명']
        
        try:
            ohlcv = stock.get_market_ohlcv_by_date(scan_start, end_date, ticker)
            if ohlcv.empty: continue
            
            # 추세 확인
            if not check_trend(ohlcv): continue
            
            # 패턴 확인
            contractions, last_depth = find_contractions(ohlcv, min_contractions)
            
            if contractions:
                # 거래량 확인
                vol_ma50 = ohlcv['거래량'].iloc[-50:].mean()
                vol_recent = ohlcv['거래량'].iloc[-5:].mean()
                vol_ratio = vol_recent / vol_ma50 if vol_ma50 > 0 else 1.0
                vol_dry_up = vol_ratio < 0.8
                
                print(f" -> [발견] {name}: {len(contractions)}T, Last {last_depth*100:.1f}%")
                
                results.append({
                    'date': end_date,
                    'ticker': ticker,
                    'name': name,
                    'market': row['Market'],
                    'close': ohlcv['종가'].iloc[-1],
                    'contractions_cnt': len(contractions),
                    'last_depth_pct': round(last_depth*100, 2),
                    'vol_dry_up': vol_dry_up,
                    'vol_ratio': round(vol_ratio, 2)
                })
                
        except Exception as e:
            continue
        
        time.sleep(0.05)
        
    # 3. 저장
    if results:
        res_df = pd.DataFrame(results)
        res_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n[완료] 총 {len(res_df)}개 종목 발견. 저장: {output_file}")
    else:
        print("\n[완료] 조건에 맞는 종목 없음.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='VCP Scanner Skill')
    parser.add_argument('--lookback', type=int, default=50, help='상승률 산정 기간 (일)')
    parser.add_argument('--top_n', type=int, default=30, help='시장별 선정 종목 수')
    parser.add_argument('--min_contraction', type=int, default=2, help='최소 축소 횟수')
    parser.add_argument('--output', type=str, default='vcp_scan_result.csv', help='결과 저장 경로')
    
    args = parser.parse_args()
    
    run_vcp_scan(args.lookback, args.top_n, args.min_contraction, args.output)

