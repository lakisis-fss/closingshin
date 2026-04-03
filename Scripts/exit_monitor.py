import json
import os
import pandas as pd
from datetime import datetime, timedelta
import logging
import FinanceDataReader as fdr
import sys
from plyer import notification
import pb_utils
import requests

# Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOG_FILE = os.path.join(DATA_DIR, 'exit_monitor.log')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Setup Logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8', mode='a'),
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )

def load_config_from_pb():
    """PocketBase에서 설정을 가져옵니다."""
    try:
        existing = pb_utils.query_pb("settings", filter_str="key='config'")
        if existing:
            return existing[0].get('value', {})
        return {}
    except Exception as e:
        print(f"Failed to load config from PB: {e}")
        return {}

def trigger_alert(title, message, config):
    logging.info(f"ALERT TRIGGERED: {title} - {message}")
    try:
        if config.get('desktop_notification', True):
            notification.notify(
                title=title,
                message=message,
                app_name='ClosingSHIN',
                timeout=10
            )
    except Exception as e:
        logging.error(f"Failed to send desktop notification: {e}")

def load_portfolio_from_pb():
    """PocketBase에서 포트폴리오 데이터를 가져옵니다."""
    try:
        records = pb_utils.query_pb("portfolio", limit=1000)
        # Convert PB names to locally expected keys
        for r in records:
            # Flexible mapping for both camelCase and snake_case
            r['ticker'] = r.get('ticker') or r.get('code')
            r['buyPrice'] = r.get('buyPrice') or r.get('buy_price')
            r['buyDate'] = r.get('buyDate') or r.get('buy_date')
            r['exitConditions'] = r.get('exitConditions') or r.get('exit_conditions')
            r['simulation'] = r.get('simulation') or r.get('simulation_data') or {}
        return records
    except Exception as e:
        logging.error(f"Failed to load portfolio from PB: {e}")
        return []

def get_current_price(ticker):
    """
    PB와 FDR을 동기화하여 최적의 현재가를 가져옵니다.
    """
    return pb_utils.get_synchronized_price(ticker)

def check_conditions(portfolio, config):
    alerts = []
    
    for item in portfolio:
        # Skip if already closed 
        if item.get('simulation', {}).get('status') == 'CLOSED':
            continue
            
        conditions = item.get('exitConditions')
        if not conditions:
            continue
            
        ticker = str(item.get('ticker', '')).zfill(6)
        name = item.get('name', ticker)
        buy_price = float(item.get('buyPrice') or 0)
        buy_date_str = item.get('buyDate', '')
        
        if not buy_date_str or buy_price <= 0:
            continue
            
        current_price = get_current_price(ticker)
        if current_price is None:
            continue
            
        pnl_pct = (current_price / buy_price - 1) * 100
        
        # 1. Stop Loss
        sl_pct = conditions.get('stopLossPercent')
        if sl_pct and sl_pct != '' and pnl_pct <= -abs(float(sl_pct)):
            alerts.append({
                'title': f"[Stop Loss] {name}",
                'message': f"PnL: {pnl_pct:+.2f}%\nCurrent Price: {current_price:,.0f}"
            })
            
        # 2. Take Profit
        tp_pct = conditions.get('takeProfitPercent')
        if tp_pct and tp_pct != '' and pnl_pct >= float(tp_pct):
            alerts.append({
                'title': f"[Take Profit] {name}",
                'message': f"PnL: {pnl_pct:+.2f}%\nCurrent Price: {current_price:,.0f}"
            })
            
        # 3. Time Cut
        time_cut = conditions.get('timeCutDays')
        if time_cut and time_cut != '':
            try:
                date_part = buy_date_str.split('T')[0]
                buy_dt = datetime.strptime(date_part, '%Y-%m-%d')
                hold_days = (datetime.now() - buy_dt).days
                if hold_days >= int(time_cut):
                    alerts.append({
                        'title': f"[Time Cut] {name}",
                        'message': f"Hold: {hold_days} days\nPnL: {pnl_pct:+.2f}%"
                    })
            except Exception: pass
            
    return alerts

def main():
    setup_logging()
    logging.info("Starting exit monitor...")
    
    config = load_config_from_pb()
    portfolio = load_portfolio_from_pb()
    
    if not portfolio:
        logging.info("No active portfolio items to monitor.")
        return

    alerts = check_conditions(portfolio, config)
    
    if alerts:
        for alert in alerts:
            trigger_alert(alert['title'], alert['message'], config)
        
        # Also recalculate portfolio status after alerts
        try:
            import importlib
            # numeric filenames require import_module
            portfolio_calc = importlib.import_module("07_calc_portfolio")
            portfolio_calc.calculate_portfolio()
        except Exception as e:
            logging.error(f"Failed to trigger portfolio calculation: {e}")
    else:
        logging.info("No exit conditions met.")

if __name__ == "__main__":
    main()
