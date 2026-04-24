import os
import csv
import json
import time
import glob
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import argparse
import sys
import pb_utils
import requests
import google.generativeai as genai

# Windows Console Encoding Fix
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path=env_path)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def setup_gemini():
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY missing.")
        return None
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel('gemini-2.0-flash')

def analyze_articles_batch(model, articles, retries=3):
    """여러 기사를 한 번에 묶어서 분석 요청 (속도 최적화)"""
    items_text = ""
    for idx, art in enumerate(articles):
        items_text += f"--- ARTICLE {idx+1} ---\nStock: {art.get('name')}\nTitle: {art.get('title')}\nDesc: {art.get('description')}\n\n"

    prompt = f"""
    Analyze following {len(articles)} stock news articles.
    {items_text}
    
    Return a JSON ARRAY of objects, one for each article in order.
    Each object must have: sentiment_score (-1 to 1), sentiment_label, impact_intensity (1-5), trading_signal, reason.
    *IMPORTANT*: Write 'sentiment_label' and 'reason' in Korean language.
    Respond ONLY with the JSON array.
    """
    
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            
            results = json.loads(text)
            if isinstance(results, list) and len(results) == len(articles):
                return results
            else:
                # 개수가 안 맞으면 에러로 간주하고 재시도
                print(f"  [Warning] Batch count mismatch. Retrying...")
                continue
        except Exception as e:
            if "429" in str(e):
                wait_time = (attempt + 1) * 10
                print(f"  [Wait] Rate limit hit (429). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"  [Error] Batch Analysis failed: {e}")
                break
    return [None] * len(articles)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str, default=None)
    args = parser.parse_args()
    date_str = args.date if args.date else datetime.now().strftime("%Y%m%d")
    
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    filter_str = f'date ~ "{formatted_date}"'
    
    # Get unprocessed news from 'news_reports' collection
    rows = pb_utils.query_pb("news_reports", filter_str=filter_str, limit=500)
    if not rows:
        print(f"No news found in PB for {date_str}.")
        return

    model = setup_gemini()
    if not model: return

    total_rows = len(rows)
    print(f"Analyzing {total_rows} articles in batch mode...")
    pb_utils.update_scan_progress(5, 0, total_rows, f"AI 뉴스 분석 시작 (배치 모드)...")
    
    batch_size = 5 # 5개씩 묶어서 처리
    for i in range(0, total_rows, batch_size):
        batch = rows[i:i+batch_size]
        current_idx = min(i + batch_size, total_rows)
        
        print(f"[{current_idx}/{total_rows}] Analyzing batch of {len(batch)}...")
        pb_utils.update_scan_progress(5, current_idx, total_rows, f"AI 뉴스 분석 중 (배치)... ({current_idx}/{total_rows})")
        
        batch_results = analyze_articles_batch(model, batch)
        
        for res_idx, analysis in enumerate(batch_results):
            if not analysis: continue
            
            row = batch[res_idx]
            name = row.get('name', 'Unknown')
            ticker = row.get('ticker') or row.get('code')
            link = row.get('link')
            
            payload = {
                "date": row['date'],
                "ticker": ticker,
                "target_stock": name,
                "title": row.get('title'),
                "link": link,
                "sentiment_score": float(analysis.get('sentiment_score') or 0),
                "sentiment_label": analysis.get('sentiment_label', ''),
                "reason": analysis.get('reason', '')
            }
            pb_utils.upsert_to_pb("news_analysis", payload, f'link="{link}"')
        
        # API 부하 분산을 위한 아주 짧은 대기
        time.sleep(0.5)

    print("Gemini Analysis Complete.")
    pb_utils.update_scan_progress(5, total_rows, total_rows, "AI 뉴스 분석 완료", "running")

if __name__ == "__main__":
    main()
