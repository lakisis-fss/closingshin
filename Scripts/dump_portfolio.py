import pb_utils
import json
import os
import sys

# Windows Console Encoding Fix
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

records = pb_utils.query_pb("portfolio", limit=100)
print(f"Total Portfolio Records: {len(records)}")
for r in records:
    ticker = r.get('ticker') or r.get('code')
    name = r.get('name')
    status = r.get('simulation_data', {}).get('status')
    print(f" {str(ticker).zfill(6)} - {name} - Status: {status}")
