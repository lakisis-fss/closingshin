from pocketbase import PocketBase
import sys
import os

# Add Scripts to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Scripts'))
try:
    from Scripts import pb_utils
    pb = pb_utils.get_pb_client()
except:
    pb = PocketBase('http://127.0.0.1:8090')

try:
    # 1. Latest date from vcp_reports
    r = pb.collection('vcp_reports').get_list(1, 1, {"sort": "-date"})
    if not r.items:
        print("Latest Scan Date: None")
    else:
        latest_date = r.items[0].date
        print(f"Latest Scan Date: {latest_date}")
        
        # 2. Check 020000 in this date
        r2 = pb.collection('vcp_reports').get_list(1, 1, {
            "filter": f'ticker = "020000" && date = "{latest_date}"'
        })
        if r2.items:
            print(f"  Found in vcp_reports: {r2.items[0].close}")
        else:
            print(f"  NOT found in vcp_reports for {latest_date}")
            
except Exception as e:
    print(f"Error: {e}")
