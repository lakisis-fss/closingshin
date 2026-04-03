import os
import sys
import json
import csv

# Add Scripts directory to path
sys.path.append(os.path.abspath('Scripts'))
import pb_utils

def migrate_config():
    config_path = 'Scripts/data/config.json'
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            pb_utils.upsert_to_pb('settings', {'key': 'config', 'value': data}, 'key="config"')
            print("[MIGRATE] config.json moved to settings.")
        except Exception as e:
            print(f"[MIGRATE] Error in config: {e}")

def migrate_target_lists():
    # Find target list CSVs
    data_dir = 'Scripts/data'
    target_files = [f for f in os.listdir(data_dir) if f.startswith('target_list_') and f.endswith('.csv')]
    
    # Also look for target_list.csv (the default one)
    if os.path.exists(os.path.join(data_dir, 'target_list.csv')):
        target_files.append('target_list.csv')
        
    for f_name in target_files:
        f_path = os.path.join(data_dir, f_name)
        try:
            # Read CSV as list of dicts
            with open(f_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # Save to settings with key as filename (to distinguish history)
            key_name = f_name.replace('.csv', '')
            pb_utils.upsert_to_pb('settings', {'key': key_name, 'value': rows}, f'key="{key_name}"')
            print(f"[MIGRATE] {f_name} moved to settings as '{key_name}'.")
        except Exception as e:
            print(f"[MIGRATE] Error in {f_name}: {e}")

if __name__ == "__main__":
    migrate_config()
    migrate_target_lists()
    print("[MIGRATE] Final migration completed.")
