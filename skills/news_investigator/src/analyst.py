import os
import json
import time
import google.generativeai as genai

def setup_gemini(api_key):
    if not api_key:
        print("Error: Google API Key not provided.")
        return None
    
    genai.configure(api_key=api_key)
    # Use a model that supports JSON mode if available, or just standard flash model
    model = genai.GenerativeModel('gemini-2.0-flash') 
    return model

def analyze_article(model, stock_name, title, description):
    prompt = f"""
    당신은 주식 시장 전문 분석가입니다. 다음 뉴스 기사를 읽고 투자자에게 필요한 5가지 핵심 정보를 JSON 포맷으로 출력하세요.

    **분석 기준:**
    1. **Sentiment Score (`sentiment_score`)**: -1.0 (악재) ~ 0 (중립) ~ 1.0 (호재)
    2. **Impact Intensity (`impact_intensity`)**: Low, Medium, High, Critical
    3. **Time Horizon (`time_horizon`)**: Short-term, Mid-term, Long-term
    4. **News Type (`news_type`)**: Fact, Disclosure, Earnings, Rumor, Expectation
    5. **Key Drivers (`key_drivers`)**: 관련된 핵심 테마나 키워드 리스트 (예: HBM, 2차전지 등)
    6. **Trading Signal (`trading_signal`)**: Buy, Sell, Watch, Ignore
    7. **Reason (`reason`)**: 위 판단에 대한 한 줄 요약 (한국어)

    **입력 데이터:**
    *   종목명: {stock_name}
    *   기사 제목: {title}
    *   기사 요약: {description}

    **출력 형식 (JSON only):**
    {{
      "target_stock": "{stock_name}",
      "sentiment_score": 0.0,
      "sentiment_label": "...",
      "impact_intensity": "...",
      "time_horizon": "...",
      "news_type": "...",
      "key_drivers": ["..."],
      "trading_signal": "...",
      "reason": "..."
    }}
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        print(f"Error analyzing article '{title}': {e}")
        return None

def analyze_news_list(news_list, api_key):
    """
    Analyzes a list of news items using Gemini API.
    Returns the list with analysis results appended.
    """
    model = setup_gemini(api_key)
    if not model:
        return news_list # Return original list if setup fails

    analyzed_results = []
    total = len(news_list)
    print(f"Analyzing {total} articles sentiment...")
    
    for i, row in enumerate(news_list):
        print(f"[{i+1}/{total}] Analyzing {row['name']} - {row['title'][:30]}...")
        
        analysis = analyze_article(model, row['name'], row['title'], row['description'])
        
        if analysis:
            # Merge original data with analysis
            combined = {**row, **analysis}
            # Handle list to string for CSV
            if isinstance(combined.get('key_drivers'), list):
                combined['key_drivers'] = ", ".join(combined['key_drivers'])
            
            analyzed_results.append(combined)
        else:
            # If analysis fails, keep original row but fill analysis fields with empty/defaults
            # Or just append raw row, but better to structure it.
            # For now, let's just append the row as is, or maybe skip? 
            # Let's append with empty analysis fields to keep the data.
            analyzed_results.append(row)
        
        # Rate limiting
        time.sleep(1) 

    return analyzed_results
