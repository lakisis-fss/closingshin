import os
import glob
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PB_URL = os.getenv("PB_URL", "http://127.0.0.1:8090")
PB_EMAIL = os.getenv("PB_EMAIL")
PB_PASSWORD = os.getenv("PB_PASSWORD")

def migrate_images():
    print(f"Connecting to {PB_URL} for image migration...")
    
    # Auth
    login_url = f"{PB_URL}/api/collections/_superusers/auth-with-password"
    r = requests.post(login_url, json={"identity": PB_EMAIL, "password": PB_PASSWORD})
    if not r.ok:
        print("Auth failed.")
        return
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Scan images
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    chart_root = os.path.join(BASE_DIR, "Scripts/results/charts")
    date_dirs = sorted(glob.glob(os.path.join(chart_root, "*")))
    
    for date_path in date_dirs:
        date_str = os.path.basename(date_path)
        if not date_str.isdigit() or len(date_str) != 8:
            continue
            
        iso_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} 00:00:00.000Z"
        print(f"Processing date: {date_str}...")
        
        image_files = glob.glob(os.path.join(date_path, "*.png"))
        for img_path in image_files:
            filename = os.path.basename(img_path)
            # market_name_ticker.png
            try:
                parts = filename.replace(".png", "").split("_")
                if len(parts) < 3:
                     # fallback
                     market = "Unknown"
                     name = parts[0]
                     ticker = parts[1] if len(parts) > 1 else "0"
                else:
                    market = parts[0]
                    name = parts[1]
                    ticker = parts[2]
                
                # Check duplicate (skip if already exists)
                filter_str = f'date = "{iso_date}" && ticker = "{ticker}"'
                check_r = requests.get(f"{PB_URL}/api/collections/vcp_charts/records", headers=headers, params={"filter": filter_str})
                if check_r.ok and check_r.json().get("totalItems", 0) > 0:
                    # print(f"  Skipping duplicate: {filename}")
                    continue
                
                # Upload
                print(f"  Uploading {filename}...")
                with open(img_path, "rb") as f:
                    payload = {
                        "date": iso_date,
                        "market": market,
                        "name": name,
                        "ticker": ticker
                    }
                    files = {
                        "file": (filename, f, "image/png")
                    }
                    up_r = requests.post(f"{PB_URL}/api/collections/vcp_charts/records", headers=headers, data=payload, files=files)
                    if not up_r.ok:
                         print(f"  Failed: {up_r.text}")
                         
            except Exception as e:
                print(f"  Error processing {filename}: {e}")

    print("Migration Complete!")

if __name__ == "__main__":
    migrate_images()
