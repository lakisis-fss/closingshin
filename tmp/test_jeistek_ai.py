import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Scripts'))
import pb_utils
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

def test_analyze():
    ticker = '090470'
    target_date = '2026-04-24'
    
    # 1. 뉴스 1개 가져오기
    news_items = pb_utils.query_pb('news_reports', filter_str=f'ticker="{ticker}" && date~"{target_date}"')
    if not news_items:
        print("No news found for Jeistek.")
        return
    
    item = news_items[0]
    name = item.get('name')
    title = item.get('title')
    description = item.get('description')
    
    print(f"--- Testing Analysis for: {title} ---")
    
    prompt = f"""
    Analyze stock news for '{name}'.
    Title: {title}
    Desc: {description}
    Return JSON: sentiment_score (-1 to 1), sentiment_label, impact_intensity (1-5), trading_signal, reason.
    *IMPORTANT*: Write 'sentiment_label' and 'reason' in Korean language.
    """
    
    try:
        response = model.generate_content(prompt)
        print("Raw Response Received.")
        text = response.text
        print(f"Response Text: {text}")
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        
        result = json.loads(text)
        print("\n--- Parsed JSON Result ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Analysis Failed: {e}")

if __name__ == "__main__":
    test_analyze()
