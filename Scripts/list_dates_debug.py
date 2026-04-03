import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def check():
    print("Listing All Unique Dates in vcp_reports...")
    recs = pb_utils.query_pb('vcp_reports', limit=1000)
    if not recs:
        print("No records found.")
        return
    
    dates = sorted(list(set([str(r.get('date'))[:10] for r in recs if r.get('date')])))
    for d in dates:
        print(f"Date: {d}")

if __name__ == "__main__":
    check()
