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

def analyze_article(model, name, title, description):
    prompt = f"""
    Analyze stock news for '{name}'.
    Title: {title}
    Desc: {description}
    Return JSON: sentiment_score (-1 to 1), sentiment_label, impact_intensity (1-5), trading_signal, reason.
    *IMPORTANT*: Write 'sentiment_label' and 'reason' in Korean language.
    """
    try:
        response = model.generate_content(prompt)
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        return json.loads(text)
    except: return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str, default=None)
    args = parser.parse_args()
    date_str = args.date if args.date else datetime.now().strftime("%Y%m%d")
    
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    filter_str = f'date ~ "{formatted_date}"'
    
    # Get unprocessed news from 'news_reports' collection
    rows = pb_utils.query_pb("news_reports", filter_str=filter_str, limit=100)
    if not rows:
        print(f"No news found in PB for {date_str}.")
        return

    model = setup_gemini()
    if not model: return

    total_rows = len(rows)
    print(f"Analyzing {total_rows} articles...")
    pb_utils.update_scan_progress(5, 0, total_rows, f"AI 뉴스 분석 시작... (0/{total_rows})")
    for i, row in enumerate(rows):
        name = row.get('name', 'Unknown')
        ticker = row.get('ticker') or row.get('code')
        link = row.get('link')

        print(f"[{i+1}/{total_rows}] Analyzing {name}...")
        pb_utils.update_scan_progress(5, i+1, total_rows, f"AI 뉴스 분석 중... ({i+1}/{total_rows})")
        analysis = analyze_article(model, name, row.get('title'), row.get('description'))
        
        if analysis:
            payload = {
                "date": row['date'],
                "ticker": ticker,
                "target_stock": name,  # Added missing field
                "title": row.get('title'),
                "link": link,
                "sentiment_score": float(analysis.get('sentiment_score') or 0),
                "sentiment_label": analysis.get('sentiment_label', ''),
                "reason": analysis.get('reason', '') # Changed from 'summary' to 'reason'
            }
            # Upsert by link
            pb_utils.upsert_to_pb("news_analysis", payload, f'link="{link}"')
            time.sleep(1)

    print("Gemini Analysis Complete.")
    pb_utils.update_scan_progress(5, total_rows, total_rows, "AI 뉴스 분석 완료", "running")

if __name__ == "__main__":
    main()
