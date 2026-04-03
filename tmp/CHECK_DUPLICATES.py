import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils

def check_duplicates(ticker):
    recs = pb_utils.query_pb('vcp_reports', filter_str=f'ticker="{ticker}"', limit=100)
    print(f"Ticker: {ticker}")
    for r in recs:
        print(f"  ID: {r['id']} | Date: {r['date']} | Name: {r['name']}")

if __name__ == "__main__":
    check_duplicates("001720")
