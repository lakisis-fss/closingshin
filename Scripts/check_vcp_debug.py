import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def check():
    print("Checking Latest 10 VCP Reports...")
    recs = pb_utils.query_pb('vcp_reports', sort='-date', limit=10)
    print(f"Found {len(recs)} records total.")
    
    for r in recs:
        print(f"ID: {r.get('id')}, Date: {r.get('date')}, UserDate: {r.get('user_date')}, Stock: {r.get('name')} ({r.get('ticker')})")

if __name__ == "__main__":
    check()
