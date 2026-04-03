import pb_utils
import json
records = pb_utils.query_pb("portfolio", limit=100)
for r in records:
    print(f"{r.get('ticker') or r.get('code')} - {r.get('name')} - Status: {r.get('simulation_data', {}).get('status')}")
