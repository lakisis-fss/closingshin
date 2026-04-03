import os
import sys
import json

# Add the Scripts directory to the path so we can import pb_utils
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))

import pb_utils

def check_gigavis_id_7488():
    id = "74880c5f2b23429"
    print(f"Checking for ID: {id} in portfolio...")
    recs = pb_utils.query_pb("portfolio", filter_str=f'id="{id}"')
    if recs:
        print(f"Found record: {json.dumps(recs[0], indent=2, ensure_ascii=False)}")
    else:
        print("Not found.")

if __name__ == "__main__":
    check_gigavis_id_7488()
