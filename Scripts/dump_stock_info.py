import json
from pb_utils import query_pb
recs = query_pb('stock_infos', limit=1)
if recs:
    print(json.dumps(recs[0], ensure_ascii=False, indent=2))
else:
    print("None")
