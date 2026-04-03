from pb_utils import query_pb
recs = query_pb("stock_infos", limit=10)
print(f"Found {len(recs)} stock_infos")
for r in recs:
    print(r)
