import sys
import os
# Add the directory containing Scripts to sys.path
sys.path.append(r'e:\Downloads\Antigravity Project\ClosingSHIN\Scripts')
import pb_utils
import json

def check_data():
    date_str = "2026-03-19"
    formatted_date = f"{date_str} 00:00:00.000Z"
    filter_str = f'date = "{formatted_date}"'
    
    print(f"Checking stock_infos for {date_str}...")
    try:
        recs = pb_utils.query_pb('stock_infos', filter_str=filter_str, limit=5)
        if not recs:
            print("No records found in stock_infos.")
        else:
            for r in recs:
                # Fields check: per, pbr, bps, dividend_yield, inst_net_5d, frgn_net_5d
                print(f"Ticker: {r.get('ticker')}, Name: {r.get('name')}, PER: {r.get('per')}, PBR: {r.get('pbr')}, Inst_5d: {r.get('inst_net_5d')}")
    except Exception as e:
        print(f"Error querying stock_infos: {e}")

    print(f"\nChecking vcp_reports for {date_str}...")
    try:
        recs_vcp = pb_utils.query_pb('vcp_reports', filter_str=filter_str, limit=5)
        if not recs_vcp:
            print("No records found in vcp_reports.")
        else:
            for r in recs_vcp:
                print(f"Ticker: {r.get('ticker')}, Name: {r.get('name')}, RS: {r.get('relative_strength')}, Consolidation: {r.get('consolidation_weeks')}")
    except Exception as e:
        print(f"Error querying vcp_reports: {e}")

if __name__ == "__main__":
    check_data()
