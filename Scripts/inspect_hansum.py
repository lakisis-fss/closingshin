import pb_utils
import json
import os
import sys

# Windows Console Encoding Fix
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

records = pb_utils.query_pb("portfolio", filter_str='ticker="020000"', limit=1)
if records:
    print(json.dumps(records[0], indent=2, ensure_ascii=False))
else:
    print("Ticker 020000 not found in portfolio collection.")
