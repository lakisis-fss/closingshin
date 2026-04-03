import os
import glob
import pandas as pd
import math
from datetime import datetime

# -----------------------------------------------------------------------------
# 설정
# -----------------------------------------------------------------------------
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

def calculate_supply_score_log(row):
    """
    단기 수급 점수 (Supply Score) 재계산 - Logarithmic Scale
    """
    market_cap = row.get('market_cap', 0)
    if pd.isna(market_cap) or market_cap == 0:
        return 0
        
    # Data extraction (default 0)
    inst_5 = row.get('기관_5일', 0)
    for_5 = row.get('외인_5일', 0)
    ind_5 = row.get('개인_5일', 0)
    
    inst_15 = row.get('기관_15일', 0)
    for_15 = row.get('외인_15일', 0)
    
    # NaN 처리
    if pd.isna(inst_5): inst_5 = 0
    if pd.isna(for_5): for_5 = 0
    if pd.isna(ind_5): ind_5 = 0
    if pd.isna(inst_15): inst_15 = 0
    if pd.isna(for_15): for_15 = 0

    # 1. Net Buying Logic (Smart Money Flow)
    smart_money_flow = (inst_5 * 1.5) + (for_5 * 1.5) + (inst_15 * 1.0) + (for_15 * 1.0)
    
    # 2. Individual Penalty
    if ind_5 > 0:
        smart_money_flow -= (ind_5 * 0.5)
        
    # 3. Market Cap Normalization (Intensity in Basis Points relative to Cap)
    intensity = (smart_money_flow / market_cap) * 10000
    
    # 4. Score Mapping (Logarithmic Scale)
    try:
        if intensity >= 0:
            score = 50 + (25 * math.log(1 + (intensity / 50)))
        else:
            score = 50 - (25 * math.log(1 + (abs(intensity) / 50)))
    except ValueError:
        score = 50
    
    # Cap and Floor
    score = max(0, min(100, score))
    
    return round(score, 1)

def migrate_files():
    print(f"Scanning for CSV files in: {RESULTS_DIR}")
    
    search_pattern = os.path.join(RESULTS_DIR, "stock_info_*.csv")
    files = glob.glob(search_pattern)
    
    if not files:
        print("No stock_info files found to migrate.")
        return

    print(f"Found {len(files)} files to process.")
    
    for file_path in files:
        filename = os.path.basename(file_path)
        print(f"Migrating {filename}...", end=" ")
        
        try:
            df = pd.read_csv(file_path)
            
            # 필수 컬럼 확인
            required_cols = ['market_cap', '기관_5일', '외인_5일', '개인_5일', '기관_15일', '외인_15일']
            missing = [c for c in required_cols if c not in df.columns]
            
            if missing:
                print(f"[SKIP] Missing columns: {missing}")
                continue
                
            # 점수 재계산 적용
            df['supply_score'] = df.apply(calculate_supply_score_log, axis=1)
            
            # 저장
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print("[DONE]")
            
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    migrate_files()
