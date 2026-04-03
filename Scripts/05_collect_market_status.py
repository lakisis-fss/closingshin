import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
import FinanceDataReader as fdr
import requests
import pb_utils
import pytz
import re
import warnings
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore')

# Identify current file path for debugging
print(f"--- EXECUTING FULL REPAIRED FILE: {os.path.abspath(__file__)} ---")

# KST timezone
KST = pytz.timezone('Asia/Seoul')
now_kst = datetime.now(KST)

def get_market_indices():
    results = {}
    indices = {'KOSPI': 'KS11', 'KOSDAQ': 'KQ11', 'NASDAQ': '^IXIC', 'SOX': '^SOX'}
    start_dt = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    for name, code in indices.items():
        data_found = False
        # 1. Try FinanceDataReader
        try:
            df = fdr.DataReader(code, start=start_dt)
            if df is not None and not df.empty:
                df = df.dropna(subset=['Close'])
                if len(df) >= 2:
                    last_val = float(df.iloc[-1]['Close'])
                    prev_val = float(df.iloc[-2]['Close'])
                    results[name] = {
                        'Close': last_val,
                        'Change': round(last_val - prev_val, 4),
                        'Change_Pct': round(((last_val - prev_val) / prev_val) * 100, 2)
                    }
                    data_found = True
                    print(f"  [Indices] {name} success (FDR)")
        except: pass

        # 2. Try Naver Polling API (Reliable for Real-time)
        if not data_found and name in ['KOSPI', 'KOSDAQ']:
            try:
                url = f"https://polling.finance.naver.com/api/realtime?query=SERVICE_INDEX:{name}"
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    item = data['result']['areas'][0]['datas'][0]
                    # 'nv' is price, 'cv' is change value, 'cr' is change rate
                    # Values might be numbers or strings with commas
                    def to_f(val):
                        if val is None: return 0.0
                        if isinstance(val, (int, float)): return float(val)
                        return float(str(val).replace(',', ''))

                    price = to_f(item.get('nv')) / 100.0
                    c_val = to_f(item.get('cv')) / 100.0
                    c_pct = to_f(item.get('cr'))
                    
                    # 'rf': '2' is Up, '5' is Down.
                    if item.get('rf') == '5' or item.get('rf') == '4':
                        c_val = -abs(c_val)
                        c_pct = -abs(c_pct)
                    
                    results[name] = {'Close': price, 'Change': c_val, 'Change_Pct': c_pct}
                    data_found = True
                    print(f"  [Indices] {name} success (Polling API) -> {price} ({c_pct}%)")
            except Exception as e:
                print(f"  [Indices] {name} Polling API Error: {e}")

        # 3. Fallback to Naver Scraper
        if not data_found and name in ['KOSPI', 'KOSDAQ']:
            try:
                url_code = 'KOSPI' if name == 'KOSPI' else 'KOSDAQ'
                url = f"https://finance.naver.com/sise/sise_index.naver?code={url_code}"
                res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                res.encoding = 'cp949'
                soup = BeautifulSoup(res.text, 'html.parser')
                price_el = soup.select_one("#now_value")
                change_el = soup.select_one("#change_value_and_rate")
                if price_el and change_el:
                    price = float(price_el.get_text().replace(',', ''))
                    text = change_el.get_text(strip=True)
                    # Use a better regex that includes minus signs
                    nums = re.findall(r'[-0-9.,]+', text)
                    if len(nums) >= 2:
                        c_val = float(nums[0].replace(',', ''))
                        c_pct = float(nums[1].replace(',', ''))
                        
                        # Check for "하락" or negative sign logic
                        if "하락" in text or "-" in nums[0] or "-" in nums[1]:
                            c_val, c_pct = -abs(c_val), -abs(c_pct)
                        elif "상승" in text:
                            c_val, c_pct = abs(c_val), abs(c_pct)
                            
                        results[name] = {'Close': price, 'Change': c_val, 'Change_Pct': c_pct}
                        print(f"  [Indices] {name} success (Scraper)")
                        data_found = True
            except: pass
    return results

def get_macro_indicators():
    results = {}
    # AI Insight(analysis_market.py)와 필드명을 통일하기 위해 키 이름을 조정
    macros = {
        'USD_KRW': ['USD/KRW', 'KRW/USD'], 
        'US10Y': ['US10Y', '^TNX'], 
        'WTI_OIL': ['CL=F', 'OIL_CL']
    }
    start_dt = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    for name, codes in macros.items():
        for code in codes:
            try:
                df = fdr.DataReader(code, start=start_dt)
                if df is not None and not df.empty:
                    df = df.dropna(subset=['Close'])
                    if len(df) >= 2:
                        last_val = float(df.iloc[-1]['Close'])
                        prev_val = float(df.iloc[-2]['Close'])
                        results[name] = {
                            'Close': last_val,
                            'Change': round(last_val - prev_val, 4),
                            'Change_Pct': round(((last_val - prev_val) / prev_val) * 100, 2)
                        }
                        print(f"  [Macro] {name} success ({code})")
                        break
            except: continue
    return results

def get_market_funds():
    """네이버 금융에서 예탁금 및 신용잔고 데이터를 긁어옵니다."""
    results = {'Funds': {'Customer_Deposit': 0, 'Credit_Balance': 0}}
    try:
        url = "https://finance.naver.com/sise/sise_deposit.naver"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        res.encoding = 'cp949'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 고객예탁금
        deposit_el = soup.select_one("tr:nth-child(3) td.num")
        if deposit_el:
            val = int(deposit_el.get_text().replace(',', '')) * 1000000 # 백만원 단위
            results['Funds']['Customer_Deposit'] = val
            
        # 신용융자잔고 (합계)
        credit_el = soup.select_one("tr:nth-child(8) td.num")
        if credit_el:
            val = int(credit_el.get_text().replace(',', '')) * 1000000 # 백만원 단위
            results['Funds']['Credit_Balance'] = val
            
        results['Funds']['Date'] = datetime.now().strftime("%Y-%m-%d")
        print(f"  [Funds] Success: Deposit={results['Funds']['Customer_Deposit']}")
    except Exception as e:
        print(f"  [Funds] Error: {e}")
    return results

def get_sector_etfs():
    results = {'Sectors': {}}
    target_sectors = {
        'KOSPI200': '069500', 'SEMICON': '091160', 'BATTERY': '305720', 
        'AUTO': '091170', 'IT': '102780', 'BANK': '102960', 
        'STEEL': '117680', 'SECURITIES': '102970'
    }
    try:
        url = "https://finance.naver.com/api/sise/etfItemList.nhn"
        res = requests.get(url)
        if res.status_code == 200:
            nv_data = res.json()
            items = {it['itemcode']: it for it in nv_data['result']['etfItemList']}
            for name, code in target_sectors.items():
                if code in items:
                    target = items[code]
                    results['Sectors'][name] = {
                        "Ticker": code,
                        "Close": float(target['nowVal']),
                        "Change_Pct": float(target['changeRate'])
                    }
            print(f"  [Sectors] Collected {len(results['Sectors'])} sectors from Naver.")
    except: pass
    return results

def get_investor_trends():
    results = {}
    try:
        def scrape_net(m_code):
            url = f"https://finance.naver.com/sise/sise_index.naver?code={m_code}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            res.encoding = 'cp949'
            soup = BeautifulSoup(res.text, 'html.parser')
            out = {}
            dl = soup.select_one("dl.lst_kos_info")
            if dl:
                for dd in dl.find_all("dd"):
                    txt = dd.get_text(strip=True)
                    match = re.search(r'([0-9,-]+)억', txt)
                    if match:
                        val = int(match.group(1).replace(',', '')) * 100000000
                        if "개인" in txt: out['Individual'] = val
                        elif "외국인" in txt: out['Foreigner'] = val
                        elif "기관" in txt: out['Institution'] = val
            return out
        results['KOSPI_Net'] = scrape_net('KOSPI')
        results['KOSDAQ_Net'] = scrape_net('KOSDAQ')
        print(f"  [Trends] KOSPI & KOSDAQ success.")
    except: pass
    return results

def get_naver_index_history(code, pages=4):
    """네이버 금융에서 지수 일별 시세를 직접 크롤링합니다. FDR 실패 시 폴백용."""
    history = {}
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        for page in range(1, pages + 1):
            url = f"https://finance.naver.com/sise/sise_index_day.naver?code={code}&page={page}"
            res = requests.get(url, headers=headers)
            res.encoding = 'cp949'
            soup = BeautifulSoup(res.text, 'html.parser')
            table = soup.select_one("table.type_1")
            if not table: continue
            rows = table.find_all("tr")
            for row in rows:
                date_el = row.select_one("td.date")
                number_els = row.select("td.number_1")
                if date_el and number_els:
                    date_str = date_el.get_text(strip=True)
                    price_str = number_els[0].get_text(strip=True).replace(',', '')
                    if date_str and price_str:
                        try:
                            clean_dt = datetime.strptime(date_str, "%Y.%m.%d")
                            clean_date = clean_dt.strftime("%Y-%m-%d")
                            history[clean_date] = float(price_str)
                        except: continue
    except Exception as e:
        print(f"  [History] Naver scrape error ({code}): {e}")
    return history

def get_market_history():
    results = {'History': []}
    try:
        # 1. Try FinanceDataReader first
        start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
        kospi_df = pd.DataFrame()
        kosdaq_df = pd.DataFrame()
        
        try:
            kospi_df = fdr.DataReader('KS11', start=start_date)
            kosdaq_df = fdr.DataReader('KQ11', start=start_date)
            print(f"  [History] FDR KOSPI: {len(kospi_df)}, KOSDAQ: {len(kosdaq_df)}")
        except Exception as e:
            print(f"  [History] FDR Error (Indices): {e}")

        # 2. Fallback to Naver Scraping if FDR fails or returns too little data
        kospi_hist = {}
        kosdaq_hist = {}
        
        # FDR records
        if not kospi_df.empty:
            for dt, row in kospi_df.iterrows():
                kospi_hist[dt.strftime("%Y-%m-%d")] = float(row['Close'])
        
        if not kosdaq_df.empty:
            for dt, row in kosdaq_df.iterrows():
                kosdaq_hist[dt.strftime("%Y-%m-%d")] = float(row['Close'])

        # Check if we need fallback
        if len(kospi_hist) < 5:
            print("  [History] Using Naver Scraper fallback for KOSPI")
            kospi_hist.update(get_naver_index_history('KOSPI', pages=6))
                
        if len(kosdaq_hist) < 5:
            print("  [History] Using Naver Scraper fallback for KOSDAQ")
            kosdaq_hist.update(get_naver_index_history('KOSDAQ', pages=6))
        
        # 3. Combine and sort
        common_dates = sorted(list(set(kospi_hist.keys()) & set(kosdaq_hist.keys())))
        print(f"  [History] Combined common dates: {len(common_dates)}")
        
        for dt_str in common_dates[-40:]:
            results['History'].append({
                'date': dt_str,
                'KOSPI': kospi_hist[dt_str],
                'KOSDAQ': kosdaq_hist[dt_str]
            })
            
    except Exception as e:
        print(f"  [History] Fatal error: {e}")
    
    print(f"  [History] Final collected points: {len(results['History'])}")
    return results

def save_to_pb(data):
    try:
        iso_date = datetime.now(KST).isoformat()
        
        # FINAL CHECK BEFORE SAVE
        print(f"  [PB] FINAL CHECK: History points = {len(data.get('History', []))}")
        
        # 1. market_status 전용 컬렉션에 기록
        date_only = iso_date[:10]
        filter_str = f'date >= "{date_only} 00:00:00.000Z" && date <= "{date_only} 23:59:59.999Z"'
        
        # upsert_to_pb를 사용하여 market_status 컬렉션에 저장
        # 컬렉션 스키마에 맞춰 'data' 필드에 딕셔너리 전체를 넣음
        pb_utils.upsert_to_pb("market_status", {"date": iso_date, "data": data}, filter_str)
        print("[PB] SUCCESS: Market status updated in 'market_status' collection.")

        # 2. settings 컬렉션에도 최신 상태 키로 저장 (추가 호환성용)
        pb_utils.upsert_to_pb("settings", {"key": "market_status", "value": data}, 'key="market_status"')
        print("[PB] SUCCESS: Market status mirror updated in 'settings'.")
        
    except Exception as e:
        print(f"[PB] ERROR saving market status: {e}")

def main():
    print("--- STARTING FULL REPAIRED COLLECTION ---")
    full_data = {}
    full_data.update(get_market_indices())
    full_data.update(get_macro_indicators())
    full_data.update(get_market_funds())
    full_data.update(get_sector_etfs())
    full_data.update(get_investor_trends())
    full_data.update(get_market_history())
    
    # AI Report generation
    try:
        from analysis_market import generate_market_report
        print("  [AI] Generating market report...")
        full_data['AI_Insight'] = generate_market_report(full_data)
        print("  [AI] Success.")
    except Exception as e:
        print(f"  [AI] Error generating AI Insight: {e}")
    
    save_to_pb(full_data)

if __name__ == '__main__':
    main()
