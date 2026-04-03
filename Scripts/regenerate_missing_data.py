import sys
import os
import subprocess
from datetime import datetime

# Script path
script_dir = os.path.dirname(os.path.abspath(__file__))
collector_script = os.path.join(script_dir, "06_collect_stock_data.py")

dates = []
if len(sys.argv) > 1:
    dates = sys.argv[1:]
else:
    # Default to recent 7 days
    from datetime import timedelta
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y%m%d") for i in range(7)]

for date in dates:
    print(f"[{datetime.now()}] Regenerating data for {date}...")
    cmd = [sys.executable, collector_script, "--date", date, "--parent"]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Success for {date}")
    except subprocess.CalledProcessError as e:
        print(f"Failed for {date}: {e}")
