import json
import os
import pandas as pd
from datetime import datetime, timedelta
import FinanceDataReader as fdr
import logging
import sys
import pb_utils
import requests

# Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOG_FILE = os.path.join(DATA_DIR, 'portfolio_calc.log')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)

def load_portfolio_from_pb():
    """PocketBase에서 포트폴리오 데이터를 가져옵니다."""
    try:
        records = pb_utils.query_pb("portfolio", limit=1000)
        final_records = []
        for r in records:
            # PB 필드명 호환성 처리 (ticker 또는 code)
            ticker = r.get('ticker') or r.get('code')
            if not ticker:
                continue
            
            r['ticker'] = str(ticker).zfill(6)
            r['buyPrice'] = r.get('buyPrice') or r.get('buy_price') or 0
            r['buyDate'] = r.get('buyDate') or r.get('buy_date')
            r['exitConditions'] = r.get('exitConditions') or r.get('exit_conditions')
            r['simulation'] = r.get('simulation') or r.get('simulation_data') or {}
            final_records.append(r)
            
        logging.info(f"Loaded {len(final_records)} valid portfolio items from PB.")
        return final_records
    except Exception as e:
        logging.error(f"포트폴리오 로드 실패 (PB): {e}")
        return []

def save_portfolio_status_to_pb(status_data):
    """PocketBase에 포트폴리오 상태를 저장합니다."""
    try:
        pb_token = pb_utils.get_pb_token()
        existing = pb_utils.query_pb("settings", filter_str="key='portfolio_status'")
        pb_data = {
            "key": "portfolio_status",
            "value": status_data
        }
        if existing:
            rec_id = existing[0]['id']
            requests.patch(
                f"{pb_utils.PB_URL}/api/collections/settings/records/{rec_id}",
                headers={"Authorization": f"Bearer {pb_token}"},
                json=pb_data
            )
        else:
            requests.post(
                f"{pb_utils.PB_URL}/api/collections/settings/records",
                headers={"Authorization": f"Bearer {pb_token}"},
                json=pb_data
            )
        logging.info("Portfolio status updated in PB.")
    except Exception as e:
        logging.error(f"Failed to save portfolio status to PB: {e}")

def get_current_price(ticker):
    """
    PB와 FDR을 동기화하여 최적의 현재가를 가져옵니다.
    """
    return pb_utils.get_synchronized_price(ticker)

def calculate_portfolio():
    # 1. PB에서 포트폴리오 데이터 로드
    portfolio = load_portfolio_from_pb()
    if not portfolio:
        logging.error("No portfolio items found in PB.")
        return

    total_value = 0
    total_cost = 0
    updated_items = []

    for item in portfolio:
        ticker = str(item.get('ticker', '')).zfill(6)
        name = item.get('name', 'Unknown')
        qty = int(item.get('quantity') or 0)
        
        # 필드 매핑 유연성 확보 (buy_price 또는 buyPrice)
        buy_price = float(item.get('buyPrice') or item.get('buy_price') or 0)
        
        if qty <= 0:
            logging.warning(f"  Skipping {name} ({ticker}): quantity={qty}")
            continue
        
        current_price = get_current_price(ticker)
        # get_current_price가 None을 반환할 때의 폴백 (매수가 사용)
        if current_price is None or current_price == 0:
            logging.warning(f"  Could not get current price for {name} ({ticker}), falling back to buyPrice: {buy_price}")
            current_price = buy_price
            
        current_value = qty * current_price
        cost_basis = qty * buy_price
        
        total_value += current_value
        total_cost += cost_basis
        
        pnl = current_value - cost_basis
        pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0
        
        # 시뮬레이션 상태 확인 (simulation_data 또는 simulation)
        sim_data = item.get('simulation') or item.get('simulation_data') or {}
        status = sim_data.get('status', 'OPEN')
        
        updated_items.append({
            'ticker': ticker,
            'name': name,
            'currentPrice': current_price,
            'currentValue': current_value,
            'pnl': pnl,
            'pnlPercent': pnl_pct,
            'status': status
        })
        logging.info(f"  Processed {name} ({ticker}): Current={current_price:,.0f}, P&L={pnl_pct:.2f}%")

    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
    
    for item in updated_items:
        item['weight'] = (item['currentValue'] / total_value * 100) if total_value > 0 else 0

    status_data = {
        'lastUpdated': datetime.now().isoformat(),
        'totalValue': total_value,
        'totalCost': total_cost,
        'totalPnL': total_pnl,
        'totalPnLPercent': total_pnl_pct,
        'items': updated_items
    }

    # 2. 로컬 JSON 파일에 저장 (프론트엔드 API 연동용)
    status_file = os.path.join(DATA_DIR, 'portfolio_status.json')
    try:
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=4, ensure_ascii=False)
        logging.info(f"Portfolio status saved to {status_file}")
    except Exception as e:
        logging.error(f"Failed to save portfolio status to file: {e}")

    # 3. PocketBase에도 백업 저장
    save_portfolio_status_to_pb(status_data)
    logging.info(f"Analysis complete. Total Value: {total_value:,.0f}")
    
    # 4. Update scan_progress to 'running' so news/ai can follow
    pb_utils.update_scan_progress(3, 100, 100, "수집 파이프라인 및 수익률 계산 완료", "running")

if __name__ == "__main__":
    calculate_portfolio()
