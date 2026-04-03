
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from pykrx import stock

# Add Scripts directory to path to import scanning logic
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Windows Console Encoding Fix
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Import functions from 02_scan_vcp.py
# Note: Since 02_scan_vcp.py is a script, importing might run main() if not guarded properly or if at root level.
# The user's 02_scan_vcp.py has `if __name__ == "__main__": main()`, so importing functions is safe.
try:
    # Use dynamic import or just recreate the logic to be safe and independent
    # Recreating the logic ensures we are testing the logic itself, not side effects.
    # But to be accurate, we should use the exact same logic.
    # Let's import.
    from scan_vcp_02 import check_trend, find_contractions # Adjust filename if it was renamed
except ImportError:
    # Fallback: Define the functions exactly as in 02_scan_vcp.py
    # Since I cannot easily renamed the file to be a valid module identifier if it starts with a number in some contexts without importlib.
    # It's safer to copy the logic here for diagnosis to guarantee execution without import errors.
    pass

# Copying logic from 02_scan_vcp.py for diagnosis
def check_trend(df):
    if len(df) < 200: return False, "데이터 부족 (200일 미만)"
    current_price = df['종가'].iloc[-1]
    ma50 = df['종가'].rolling(window=50).mean().iloc[-1]
    ma150 = df['종가'].rolling(window=150).mean().iloc[-1]
    ma200 = df['종가'].rolling(window=200).mean().iloc[-1]
    
    if current_price < ma200: return False, "200일선 아래 (장기 하락세)"
    if not (ma50 > ma150 > ma200): return False, "이평선 역배열 (50>150>200 미충족)"
    return True, "상승 추세"

def find_contractions(df):
    # Constants from the script
    MIN_CONTRACTIONS = 2
    MIN_DEPTH_LAST = 0.02
    MAX_DEPTH_LAST = 0.15 # Updated to 15%
    
    sub_df = df.iloc[-120:].copy()
    if len(sub_df) < 60: return [], 0, "데이터 부족", 0
    prices = sub_df['종가'].values
    peaks = []
    for i in range(5, len(prices)-5):
        if prices[i] == max(prices[i-5:i+6]):
            peaks.append((i, prices[i]))
    
    contractions = []
    if len(peaks) < 2: return contractions, 0.0, "파동 부족", 0
    
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
        if MIN_DEPTH_LAST <= valid_adjustments[-1] <= MAX_DEPTH_LAST:
            if valid_adjustments[-1] <= (valid_adjustments[-2] * 1.2): # Updated tolerance
                is_vcp = True
                
    return valid_adjustments, valid_adjustments[-1], "VCP 후보" if is_vcp else "패턴 미완성", pivot_point

TARGETS = {
    "028050": "삼성E&A",
    "028670": "팬오션",
    "290650": "엘앤씨바이오",
    "048410": "현대바이오"
}

DATE = "20260219"

def diagnose():
    output_file = "diagnosis_results.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        sys.stdout = f
        print(f"[{datetime.now()}] Diagnosing Missing VCP Targets for {DATE}")
        
        # 1. Check if they are selected as Top 30 Winners
        # Calculate 50 day return
        end_date = DATE
        start_date = (datetime.strptime(end_date, "%Y%m%d") - timedelta(days=50+20)).strftime("%Y%m%d") # Enough buffer
        
        print("\n--- 1. Performance Check (Top 30 Candidates Filter) ---")
        print("Standard: Top 30 highest gainers over last 50 days (LOOKBACK_DAYS=50)")
        
        for ticker, name in TARGETS.items():
            try:
                print(f"\nScanning {name} ({ticker})...")
                df = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
                if df.empty:
                    print(f"  -> Data not found for range {start_date}~{end_date}")
                    continue
                    
                # Calclulate 50-day return
                # Simple approximation: Close 50 days ago vs Close now
                if len(df) >= 30: # Relaxed check, just need some data
                    price_now = df['종가'].iloc[-1]
                    price_50_ago = df['종가'].iloc[0] # Approx 50 days ago if len is around 50
                    # More accurate:
                    if len(df) >= 50:
                        price_50_ago = df['종가'].iloc[-50]
                    
                    return_pct = ((price_now - price_50_ago) / price_50_ago) * 100
                    print(f"  -> 50-day return: {return_pct:.2f}% (Price: {price_50_ago} -> {price_now})")
                else:
                    print(f"  -> Not enough data for 50-day return (Rows: {len(df)})")
                    
                # 2. Check Trend
                # Need more history for trend check (200 days)
                start_date_trend = (datetime.strptime(end_date, "%Y%m%d") - timedelta(days=365)).strftime("%Y%m%d")
                df_trend = stock.get_market_ohlcv_by_date(start_date_trend, end_date, ticker)
                
                # Calculate MAs manually to ensure they exist
                df_trend['ma50'] = df_trend['종가'].rolling(window=50).mean()
                df_trend['ma150'] = df_trend['종가'].rolling(window=150).mean()
                df_trend['ma200'] = df_trend['종가'].rolling(window=200).mean()

                is_uptrend, trend_msg = check_trend(df_trend)
                print(f"  -> Trend Check: {'PASS' if is_uptrend else 'FAIL'} ({trend_msg})")
                
                if True: # Always check VCP even if trend fails, for diagnosis
                    # 3. Check VCP Pattern
                    contractions, last_depth, pattern_msg, pivot = find_contractions(df_trend)
                    print(f"  -> VCP Pattern: {'PASS' if pattern_msg == 'VCP 후보' else 'FAIL'} ({pattern_msg})")
                    if contractions:
                        print(f"    - Contractions: {[round(c*100, 1) for c in contractions]}")
                        print(f"    - Last Depth: {last_depth*100:.2f}%")
                
            except Exception as e:
                print(f"Error checking {name}: {e}")
                import traceback
                traceback.print_exc()

    # Reset stdout
    sys.stdout = sys.__stdout__
    print(f"Diagnosis complete. Results written to {output_file}")

if __name__ == "__main__":
    diagnose()
