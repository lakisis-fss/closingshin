
import os
import sys
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
# from pykrx import stock # pykrx deprecated
import time
import matplotlib.font_manager as fm
import argparse

# -----------------------------------------------------------------------------
# 설정
# -----------------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
RESULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
CHART_DIR = os.path.join(RESULT_DIR, "charts")
PROGRESS_FILE = os.path.join(DATA_DIR, "scan_progress.json")
import json
import pb_utils
import io

def update_progress(step, progress, total, message, status="running"):
    pb_utils.update_scan_progress(step, progress, total, message, status)

def parse_args():
    parser = argparse.ArgumentParser(description='VCP Chart Visualizer')
    parser.add_argument('--date', type=str, default=None,
                        help='Target date in YYYYMMDD format (default: today)')
    return parser.parse_args()

args = parse_args()
TODAY = args.date if args.date else datetime.now().strftime("%Y%m%d")

# 폰트 설정 (Windows 기준 맑은 고딕, Linux 기준 나눔고딕)
if os.name == 'nt':
    FONT_NAME = 'Malgun Gothic'
else:
    FONT_NAME = 'NanumGothic'

plt.rcParams['font.family'] = FONT_NAME
plt.rcParams['axes.unicode_minus'] = False

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_vcp_report_from_pb(target_date):
    """PocketBase에서 해당 날짜의 VCP 리포트를 가져옵니다."""
    try:
        # PB date filter (YYYY-MM-DD format expected if using date type)
        formatted_date = f"{target_date[:4]}-{target_date[4:6]}-{target_date[6:8]}"
        filter_str = f'date ~ "{formatted_date}"'
        
        records = pb_utils.query_pb("vcp_reports", filter_str=filter_str, limit=500)
        if not records:
            print(f"[Info] {target_date}의 VCP 리포트가 PB에 없습니다.")
            return None
        
        return pd.DataFrame(records)
    except Exception as e:
        print(f"[Error] PB 리포트 로드 실패: {e}")
        return None

def create_vcp_chart(ticker, name, market, report_row, save_folder):
    """
    개별 종목의 2K 해상도 VCP 차트를 생성하고 저장합니다.
    """
    try:
        # PocketBase ohlcv 컬렉션에서 데이터 수집
        df = pb_utils.fetch_pb_ohlcv(ticker, limit=260) # 차트용 250~260일
        if df is None or df.empty:
            print(f"[Skip] PB에 가격 데이터 없음: {name} ({ticker})")
            return

        # 컬럼명 정규화 (PB 소문자 또는 기존 한글 대응)
        rename_map = {
            '시가': 'Open', '고가': 'High', '저가': 'Low', '종가': 'Close', '거래량': 'Volume',
            'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'
        }
        df = df.rename(columns=lambda x: rename_map.get(x, x))
        
        # 인덱스 설정 (mplfinance 필수)
        df = df.set_index('date')
        df.index.name = 'Date'
        
        # 이동평균선 계산
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA150'] = df['Close'].rolling(window=150).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
        
        # 최근 1년치만 슬라이싱 (그리기용)
        plot_df = df.iloc[-250:] 

        # VCP 정보 텍스트 구성
        # report_row는 Pandas Series
        vcp_info = (
            f"VCP Analysis Report\n"
            f"DATE: {TODAY}\n"
            f"--------------------------------\n"
            f"T-Count (축소 횟수) : {report_row.get('contractions_count', 'N/A')}T\n"
            f"History (파동 이력) : {report_row.get('contractions_history', 'N/A')}\n"
            f"Last Depth (마지막 폭) : {report_row.get('last_depth_pct', 'N/A')}%\n"
            f"Volume Dry-Up (급감) : {'YES' if report_row.get('volume_dry_up') else 'NO'}\n"
            f"Volume Ratio (비율) : {report_row.get('vol_ratio', 'N/A')} (vs 50MA)"
        )

        # 스타일 설정
        mc = mpf.make_marketcolors(up='red', down='blue', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc, gridstyle=':', y_on_right=True)
        
        # 추가 플롯 (이평선)
        add_plots = [
            mpf.make_addplot(plot_df['MA50'], color='green', width=1.5, label='MA50'),
            mpf.make_addplot(plot_df['MA150'], color='orange', width=1.5, label='MA150'),
            mpf.make_addplot(plot_df['MA200'], color='black', width=2.0, label='MA200'),
        ]

        # 차트 파일명 정의
        filename = f"{market}_{name}_{ticker}.png"

        # Figure 생성 (2K 해상도: 2560x1440)
        fig, axes = mpf.plot(
            plot_df,
            type='candle',
            style=s,
            addplot=add_plots,
            volume=True,
            title=f"\n{name} ({ticker}) - {market}",
            figsize=(25.6, 14.4), 
            returnfig=True,
            show_nontrading=False
        )
        
        # 텍스트 박스 추가
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        axes[0].text(0.02, 0.95, vcp_info, transform=axes[0].transAxes, fontsize=16,
                    verticalalignment='top', bbox=props, fontfamily=FONT_NAME)

        # 9. Save to memory buffer instead of local file
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        
        print(f"[생성완료] {name} ({ticker}) 차트 메모리 저장됨")

        # 10. Upload to PocketBase (vcp_charts)
        try:
            from pb_utils import get_pb_token, PB_URL
            import requests
            
            token = get_pb_token()
            if token:
                iso_date = f"{TODAY[0:4]}-{TODAY[4:6]}-{TODAY[6:8]} 00:00:00.000Z"
                
                # Check duplicate
                check_url = f"{PB_URL}/api/collections/vcp_charts/records"
                filter_str = f'date = "{iso_date}" && ticker = "{ticker}"'
                r_check = requests.get(check_url, headers={"Authorization": f"Bearer {token}"}, params={"filter": filter_str})
                
                exist_id = None
                if r_check.ok and r_check.json().get("totalItems", 0) > 0:
                    exist_id = r_check.json()["items"][0]["id"]

                payload = {
                    "date": iso_date,
                    "market": market,
                    "name": name,
                    "ticker": ticker
                }
                
                # Upload buffer
                files = {"file": (filename, buf, "image/png")}
                
                if exist_id:
                    up_url = f"{PB_URL}/api/collections/vcp_charts/records/{exist_id}"
                    response = requests.patch(up_url, headers={"Authorization": f"Bearer {token}"}, data=payload, files=files)
                    if response.ok:
                        print(f"[PB 업데이트] {filename}")
                    else:
                        print(f"[PB 업데이트 실패] {filename}: {response.status_code} - {response.text}")
                else:
                    up_url = f"{PB_URL}/api/collections/vcp_charts/records"
                    response = requests.post(up_url, headers={"Authorization": f"Bearer {token}"}, data=payload, files=files)
                    if response.ok:
                        print(f"[PB 업로드] {filename}")
                    else:
                        print(f"[PB 업로드 실패] {filename}: {response.status_code} - {response.text}")
            else:
                print(f"[경고] PB 토큰 없음. {filename} PB 업로드 건너뜀.")
        except Exception as e:
            print(f"[오류] PB 업로드 실패 ({filename}): {e}")

        return True
    except Exception as e:
        print(f"[에러] {name}: {e}")
        return None

def main():
    print(f"[{datetime.now()}] VCP 차트 시각화 시작...")
    
    report_df = get_vcp_report_from_pb(TODAY)
    if report_df is None or report_df.empty:
        print(f"[오류] {TODAY} 날짜의 VCP 결과가 PB에 없습니다.")
        return
    
    total = len(report_df)
    print(f"총 {total}개 종목 차트 생성 예정.")

    for i, row in report_df.iterrows():
        ticker = str(row['ticker']).zfill(6)
        name = row['name']
        market = row.get('market') or row.get('market_name', 'KOSPI')
        
        update_progress(6, i+1, total, f"차트 생성 중... {name} ({i+1}/{total})")
        
        try:
            create_vcp_chart(ticker, name, market, row, None)
        except Exception as e:
             print(f"[메인루프 에러] {name}: {e}")
        
        time.sleep(0.5) # 과부하 방지

    print("\n[완료] 모든 차트 생성이 끝났습니다.")

if __name__ == "__main__":
    main()
