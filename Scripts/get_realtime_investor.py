
import requests
from bs4 import BeautifulSoup

def get_realtime_investor(market_code='KOSPI'):
    # KOSPI: KOSPI, KOSDAQ: KOSDAQ
    url_code = 'KOSPI' if market_code.upper() == 'KOSPI' else 'KOSDAQ'
    url = f"https://finance.naver.com/sise/sise_index.naver?code={url_code}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers)
        res.encoding = 'cp949' # Naver Finance uses cp949 usually
        soup = BeautifulSoup(res.text, 'html.parser')
        
        print(f"Status: {res.status_code}")
        
        # Select the dl list
        dl = soup.select_one("dl.lst_kos_info")
        if not dl:
             print("dl.lst_kos_info not found")
             # Fallback check
             idx = res.text.find("투자자별 매매동향")
             if idx != -1: print(f"Found keyword at {idx}")
             return {}
             
        if not dl:
             print("dl.lst_kos_info not found")
             return {}
             
        data = {}
        
        # dds contain the items
        dds = dl.find_all("dd")
        
        for dd in dds:
            text = dd.get_text(strip=True)
            # text likely like "개인-9,101억"
            
            val_str = text.replace('개인', '').replace('외국인', '').replace('기관', '').replace('억', '').replace(',', '').replace('+', '')
            
            try:
                # Remove any leftover non-digit/sign chars just in case (e.g. '상승', '하락')
                # But typically it's just number
                # Check if it corresponds to a key
                val = int(val_str)
                
                if "개인" in text: data['Individual'] = val
                elif "외국인" in text: data['Foreigner'] = val
                elif "기관" in text: data['Institution'] = val
            except:
                pass
                
        return data

    except Exception as e:
        print(f"Error scraping {market_code}: {e}")
        return None

if __name__ == "__main__":
    print("KOSPI:", get_realtime_investor('KOSPI'))
    print("KOSDAQ:", get_realtime_investor('KOSDAQ'))
