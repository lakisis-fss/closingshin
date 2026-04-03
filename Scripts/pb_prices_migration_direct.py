import os
import glob
import sqlite3
import pandas as pd
import secrets
from datetime import datetime

PB_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pb_data', 'data.db')
PRICES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'prices')

def generate_pb_id():
    return secrets.token_hex(8)[:15]

def migrate_directly():
    print(f"Connecting to database: {PB_DB_PATH}")
    conn = sqlite3.connect(PB_DB_PATH)
    c = conn.cursor()
    
    # 1. Get exact columns of ohlcv
    c.execute("PRAGMA table_info(ohlcv)")
    cols_info = c.fetchall()
    table_cols = [col[1] for col in cols_info]
    print(f"ohlcv table columns: {table_cols}")
    
    # 2. Truncate table
    print("Clearing existing data in ohlcv...")
    c.execute("DELETE FROM ohlcv")
    
    # 3. Read CSVs
    csv_files = glob.glob(os.path.join(PRICES_DIR, '*.csv'))
    print(f"Found {len(csv_files)} CSV files. Preparing for batch insert...")
    
    total_inserted = 0
    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.000Z')
    
    for idx, file_path in enumerate(csv_files):
        ticker = os.path.basename(file_path).replace('.csv', '')
        try:
            df = pd.read_csv(file_path)
            # Normalize column names to lowercase
            df.columns = [col.lower() for col in df.columns]
            
            if 'date' not in df.columns:
                continue
                
            batch_data = []
            for _, row in df.iterrows():
                date_val = str(row['date'])
                if ' ' in date_val: date_val = date_val.split(' ')[0]
                
                # Create record dict mapped to valid DB columns
                record = {}
                for col_name in table_cols:
                    if col_name == 'id': record['id'] = generate_pb_id()
                    elif col_name == 'code': record['code'] = ticker
                    elif col_name == 'date': record['date'] = f"{date_val} 00:00:00.000Z"
                    elif col_name == 'open': record['open'] = float(row['open']) if not pd.isna(row.get('open')) else 0
                    elif col_name == 'high': record['high'] = float(row['high']) if not pd.isna(row.get('high')) else 0
                    elif col_name == 'low': record['low'] = float(row['low']) if not pd.isna(row.get('low')) else 0
                    elif col_name == 'close': record['close'] = float(row['close']) if not pd.isna(row.get('close')) else 0
                    elif col_name == 'volume': record['volume'] = int(row['volume']) if not pd.isna(row.get('volume')) else 0
                    elif col_name == 'change': record['change'] = float(row['change']) if not pd.isna(row.get('change')) else 0
                    elif col_name in ['created', 'updated']: record[col_name] = now_str
                    else: record[col_name] = None
                
                batch_data.append(tuple(record[col] for col in table_cols))
            
            if batch_data:
                placeholders = ",".join(["?"] * len(table_cols))
                sql = f"INSERT INTO ohlcv ({','.join(table_cols)}) VALUES ({placeholders})"
                c.executemany(sql, batch_data)
                total_inserted += len(batch_data)
                
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            
        if (idx + 1) % 500 == 0:
            print(f"Processed {idx + 1}/{len(csv_files)} files... (Inserted {total_inserted} records)")
            conn.commit()
            
    conn.commit()
    conn.close()
    print(f"\n✅ Migration Complete! Successfully inserted {total_inserted:,} records.")

if __name__ == "__main__":
    migrate_directly()
