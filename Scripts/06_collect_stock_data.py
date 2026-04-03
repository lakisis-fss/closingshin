import os
import sys
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import argparse
import requests
import pb_utils
import io
import FinanceDataReader as fdr
from bs4 import BeautifulSoup

# Windows Console Encoding Fix
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PB_COLLECTION = "stock_infos"

def get_detailed_info(ticker, bizdate=""):
    """Naver Finance에서 상세 정보 수집 (기본 지표 및 모바일 API 기반 100일 수급)"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    data = {}
    
    # 1. 기본/기대 지표 추출 (PER, PBR, 배당수익률, EPS, BPS)
    try:
        url = f"https://finance.naver.com/item/main.naver?code={ticker}"
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'euc-kr'
        soup = BeautifulSoup(res.text, 'html.parser')

        def safe_float(selector):
            el = soup.select_one(selector)
            if el:
                try:
                    return float(el.get_text().replace(',', '').replace('%', '').replace('배', '').strip())
                except: return 0
            return 0

        data['per'], data['pbr'], data['dividend_yield'] = safe_float("#_per"), safe_float("#_pbr"), safe_float("#_dvr")
        
        # 기업실적분석 테이블에서 상세 지표 추출 (안정적인 키워드 매칭 방식 V12)
        cop_rows = soup.select(".section.cop_analysis .tb_type1 tbody tr")
        if cop_rows:
            def get_val_by_keywords(rows, keywords):
                for row in rows:
                    header = row.select_one("th")
                    if header:
                        txt = header.get_text(strip=True)
                        if any(k in txt for k in keywords):
                            tds = row.select("td")
                            # 최근 결산 연도 데이터 (보통 3~4번째 열)
                            for td in reversed(tds[:4]):
                                v = td.get_text(strip=True).replace(',', '').strip()
                                if v and v != '-' and not v.startswith('('):
                                    try: return float(v)
                                    except: continue
                return 0

            data['per'] = data.get('per') or get_val_by_keywords(cop_rows, ["PER", "주가수익비율"])
            data['pbr'] = data.get('pbr') or get_val_by_keywords(cop_rows, ["PBR", "주가순자산비율"])
            data['eps'] = get_val_by_keywords(cop_rows, ["EPS", "주당순이익"])
            data['bps'] = get_val_by_keywords(cop_rows, ["BPS", "주당순자산"])
            data['dps'] = get_val_by_keywords(cop_rows, ["주당배당금", "DPS"])
            if not data.get('dividend_yield'): 
                data['dividend_yield'] = get_val_by_keywords(cop_rows, ["배당수익률", "현금배당수익률"])
            
            # --- Fundamental Score Calculation (V13) ---
            f_score = 0
            # 1. PER (Value) - Max 30
            per = data.get('per', 0)
            if 0 < per < 15: f_score += 30
            elif 15 <= per < 30: f_score += 20
            elif 30 <= per < 50: f_score += 10
            
            # 2. PBR (Asset) - Max 30
            pbr = data.get('pbr', 0)
            if 0 < pbr < 1: f_score += 30
            elif 1 <= pbr < 2: f_score += 20
            elif 2 <= pbr < 3: f_score += 10
            
            # 3. EPS (Earnings) - Max 20
            if data.get('eps', 0) > 0: f_score += 20
            
            # 4. Dividend (Dividend) - Max 20
            if data.get('dividend_yield', 0) > 0: f_score += 20
            
            data['fundamental_score'] = f_score
            # -------------------------------------------
            
            # Debug log for significant stock
            if ticker == "323280":
                print(f"  [DEBUG] {ticker} V13 -> PER:{data.get('per')}, PBR:{data.get('pbr')}, Score:{data.get('fundamental_score')}")
    except Exception as e:
        print(f"  [Error] {ticker} Scraping: {e}")

    # 2. 투자자별 매매동향 (모바일 API 사용 - 페이지네이션 100일 수집)
    try:
        if not bizdate:
            bizdate = datetime.now().strftime("%Y%m%d")
        
        inst_vals, foreign_vals, indiv_vals = [], [], []
        current_date = bizdate
        
        for _ in range(5): # 20일씩 5번 = 100일
            api_url = f"https://m.stock.naver.com/api/stock/{ticker}/trend?pageSize=20&bizdate={current_date}"
            api_headers = headers.copy()
            api_headers['Referer'] = 'https://m.stock.naver.com/'
            
            res = requests.get(api_url, headers=api_headers, timeout=10)
            if res.status_code != 200: break
            
            items = res.json()
            if not items: break
            
            for item in items:
                price = int(item.get('closePrice', '0').replace(',', ''))
                if price == 0: continue
                
                # 수량 파싱
                def q_parse(v): return int(v.replace(',', '').replace('+', '')) if v else 0
                
                inst_q = q_parse(item.get('organPureBuyQuant'))
                frgn_q = q_parse(item.get('foreignerPureBuyQuant'))
                indi_q = q_parse(item.get('individualPureBuyQuant'))
                
                # 백만 원 단위 환산
                inst_vals.append((inst_q * price) / 1_000_000)
                foreign_vals.append((frgn_q * price) / 1_000_000)
                indiv_vals.append((indi_q * price) / 1_000_000)
            
            # [V4] 최신일 기준 종가 및 등락률 추출 (첫 번째 호출 시에만 저장)
            if not data.get('close'):
                latest = items[0]
                latest_date = latest.get('bizdate')
                
                # [Surgical Fix] 요청한 bizdate와 리턴된 latest_date가 일치하는지 검증
                # 만약 네이버 API가 아직 오늘 데이터를 업데이트하지 않았으면, 어제 날짜를 오늘 날짜로 잘못 저장하는 것을 방지
                if bizdate and latest_date != bizdate:
                    print(f"    [Warning] {ticker} Date Mismatch: Requested {bizdate}, but got {latest_date}. Skipping price_change_pct update.")
                    data['price_change_pct'] = 0
                    data['close'] = 0
                else:
                    latest_p = int(latest.get('closePrice', '0').replace(',', ''))
                    diff = int(latest.get('compareToPreviousClosePrice', '0').replace(',', ''))
                    # 등락률 계산: (변동폭 / (종가 - 변동폭)) * 100
                    if latest_p - diff != 0:
                        change_pct = (diff / (latest_p - diff)) * 100
                        data['price_change_pct'] = round(change_pct, 2)
                    else:
                        data['price_change_pct'] = 0
                    data['close'] = latest_p

            # 다음 페이지를 위해 마지막 날짜 업데이트 (형식: 20260319)
            current_date = items[-1].get('bizdate')
            if len(inst_vals) >= 100: break
            time.sleep(0.05)

        # 기간별 누적 합계 계산 (5, 15, 30, 50, 100일)
        periods = [5, 15, 30, 50, 100]
        for p in periods:
            data[f'inst_net_{p}d'] = round(sum(inst_vals[:p]), 2)
            data[f'foreign_net_{p}d'] = round(sum(foreign_vals[:p]), 2)
            data[f'indiv_net_{p}d'] = round(sum(indiv_vals[:p]), 2)

        # 수급 점수 계산 (V5: 쌍끌이 우대 및 개인 페널티 강화)
        score = 0
        p_weights = {5: 15, 15: 20, 30: 25, 50: 20, 100: 20} # 합계 100
        for p, w in p_weights.items():
            inst = data.get(f'inst_net_{p}d', 0)
            frgn = data.get(f'foreign_net_{p}d', 0)
            indi = data.get(f'indiv_net_{p}d', 0)
            
            p_score = 0
            # 1. 기관/외인 기여도 계산
            if inst > 0 and frgn > 0:
                p_score = w  # 동반 매수 (쌍끌이) 100%
            elif inst + frgn > 0:
                p_score = w * 0.5  # 어느 한쪽이라도 매수세가 강하면 50%
            
            # 2. 개인(Retail) 페널티 적용
            # 개인이 사고 있다면 (Pros are selling to Retail), 해당 기간 점수에 페널티
            if p_score > 0 and indi > 0:
                p_score *= 0.7  # 30% 감점
                
            score += p_score
        
        data['supply_score'] = int(round(score))

    except Exception as e:
        print(f"  [Error] {ticker} Investor API: {e}")

    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str, default=datetime.now().strftime("%Y%m%d"))
    args = parser.parse_args()
    
    formatted_date = f"{args.date[:4]}-{args.date[4:6]}-{args.date[6:8]} 00:00:00.000Z"

    # 1. Fetch tickers from vcp_reports for today
    vcp_targets = pb_utils.query_pb("vcp_reports", filter_str=f'date="{formatted_date}"', limit=200)
    target_list = []
    for item in vcp_targets:
        target_list.append({
            'ticker': item['ticker'],
            'name': item['name']
        })
    
    # 2. Fetch tickers from portfolio (Active only)
    try:
        portfolio_items = pb_utils.query_pb("portfolio", limit=500)
        portfolio_tickers = {item['ticker'] for item in portfolio_items if item.get('simulation_data', {}).get('status') != 'CLOSED'}
        
        # Add portfolio tickers that are not in VCP targets
        existing_tickers = {item['ticker'] for item in target_list}
        for item in portfolio_items:
            ticker = str(item.get('ticker') or item.get('code', '')).zfill(6)
            if ticker and ticker not in existing_tickers and item.get('simulation_data', {}).get('status') != 'CLOSED':
                target_list.append({
                    'ticker': ticker,
                    'name': item.get('name', 'Portfolio Item')
                })
                existing_tickers.add(ticker)
    except Exception as e:
        print(f"  [Warning] Failed to fetch portfolio items: {e}")

    if not target_list:
        print("No targets found for today in PB (VCP or Portfolio).")
        return

    total = len(target_list)
    print(f"Collecting detailed info for {total} stocks...")
    for i, item in enumerate(target_list, 1):
        ticker = item['ticker']
        name = item['name']
        print(f" Processing {name} ({ticker})... ({i}/{total})")
        
        # Update progress in PocketBase
        pb_utils.update_scan_progress(1, i, total, f"데이터 수집 중: {name} ({i}/{total})", "running")
        
        bizdate = args.date.replace('-', '') if args.date else ""
        info = get_detailed_info(ticker, bizdate=bizdate)
        
        payload = {
            "date": formatted_date,
            "ticker": ticker,
            "name": name,
            "close": info.get('close', 0),
            "price_change_pct": info.get('price_change_pct', 0),
            "PER": info.get('per', 0),
            "PBR": info.get('pbr', 0),
            "EPS": info.get('eps', 0),
            "BPS": info.get('bps', 0),
            "DIV": info.get('dividend_yield', 0),
            "DPS": info.get('dps', 0),
            "inst_net_5d": info.get('inst_net_5d', 0),
            "foreign_net_5d": info.get('foreign_net_5d', 0),
            "indiv_net_5d": info.get('indiv_net_5d', 0),
            "inst_net_15d": info.get('inst_net_15d', 0),
            "foreign_net_15d": info.get('foreign_net_15d', 0),
            "indiv_net_15d": info.get('indiv_net_15d', 0),
            "inst_net_30d": info.get('inst_net_30d', 0),
            "foreign_net_30d": info.get('foreign_net_30d', 0),
            "indiv_net_30d": info.get('indiv_net_30d', 0),
            "inst_net_50d": info.get('inst_net_50d', 0),
            "foreign_net_50d": info.get('foreign_net_50d', 0),
            "indiv_net_50d": info.get('indiv_net_50d', 0),
            "inst_net_100d": info.get('inst_net_100d', 0),
            "foreign_net_100d": info.get('foreign_net_100d', 0),
            "indiv_net_100d": info.get('indiv_net_100d', 0),
            "supply_score": info.get('supply_score', 0),
            "fundamental_score": info.get('fundamental_score', 0),
            "market_cap": info.get('market_cap', 0)
        }
        
        filter_str = f'ticker="{ticker}" && date="{formatted_date}"'
        pb_utils.upsert_to_pb("stock_infos", payload, filter_str)
        time.sleep(0.1)

    # 4. Final log (Reported by orchestrator later)
    print(f"[{datetime.now()}] Data collection phase completed.")

if __name__ == "__main__":
    main()
