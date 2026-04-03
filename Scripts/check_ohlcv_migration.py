import os
import glob
import pandas as pd
import sqlite3

def check_migration_status():
    pb_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pb_data', 'data.db')
    prices_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'prices')
    
    if not os.path.exists(pb_db_path):
        print(f"Error: Database not found at {pb_db_path}")
        return
        
    print("Reading PocketBase SQLite database...")
    conn = sqlite3.connect(pb_db_path)
    cursor = conn.cursor()
    
    # Check if ohlcv table exists
    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='ohlcv'")
    if cursor.fetchone()[0] == 0:
        print("Error: Table 'ohlcv' does not exist in PB database.")
        conn.close()
        return

    # Count records per code in PB
    cursor.execute("SELECT code, COUNT(*) as count FROM ohlcv GROUP BY code")
    pb_counts = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    
    print("Reading local CSV files...")
    csv_files = glob.glob(os.path.join(prices_dir, '*.csv'))
    
    mismatches = []
    total_csv_rows = 0
    total_pb_rows = sum(pb_counts.values())
    
    for file_path in csv_files:
        ticker = os.path.basename(file_path).replace('.csv', '')
        try:
            # fast row count
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            # Assuming 1 header line and maybe empty lines
            valid_lines = [l for l in lines[1:] if l.strip()]
            csv_count = len(valid_lines)
            total_csv_rows += csv_count
            
            pb_count = pb_counts.get(ticker, 0)
            
            if csv_count != pb_count:
                mismatches.append({
                    'ticker': ticker,
                    'csv_count': csv_count,
                    'pb_count': pb_count,
                    'diff': csv_count - pb_count
                })
        except Exception as e:
            print(f"Error processing {ticker}.csv: {e}")
            
    print("\n" + "="*40)
    print("📊 MIGRATION CHECK RESULTS")
    print("="*40)
    print(f"Total CSV Files Processed: {len(csv_files):,}")
    print(f"Total Valid Rows in CSVs:   {total_csv_rows:,}")
    print(f"Total Records in PB ohlcv:  {total_pb_rows:,}")
    
    if mismatches:
        print(f"\n⚠️ Found {len(mismatches)} tickers with mismatched counts.")
        print("Top 20 absolute mismatches:")
        mismatches.sort(key=lambda x: abs(x['diff']), reverse=True)
        for m in mismatches[:20]:
            print(f"  - Ticker {m['ticker']}: CSV {m['csv_count']} vs PB {m['pb_count']} (Diff: {m['diff']})")
    else:
        print("\n✅ ALL DATA MIGRATED SUCCESSFULLY!")
        print("Count matches perfectly between CSVs and PocketBase for all tickers.")
        
if __name__ == "__main__":
    check_migration_status()
