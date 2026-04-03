
import os
import json
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def generate_market_report(data):
    """
    Generates a market analysis report using Gemini AI based on the provided market data.
    
    Args:
        data (dict): The dictionary containing market status data (KOSPI, KOSDAQ, etc.)
        
    Returns:
        dict: A dictionary containing the AI's analysis with keys:
              - sentiment: "POSITIVE", "NEUTRAL", or "NEGATIVE"
              - summary: A one-sentence summary (Korean)
              - reasoning: A detailed explanation (Korean)
    """
    print("  [AI] preparing data for analysis...")
    
    if not GEMINI_API_KEY:
        print("  [AI] Error: GEMINI_API_KEY not found in environment variables.")
        return {
            "sentiment": "NEUTRAL",
            "summary": "AI 분석을 사용할 수 없습니다 (API Key 부족).",
            "reasoning": "시스템 환경 변수에 GEMINI_API_KEY가 설정되지 않았습니다."
        }

    # 1. Wrapper: Format Data for AI Prompt
    try:
        prompt_text = _create_prompt(data)
    except Exception as e:
        print(f"  [AI] Error creating prompt: {e}")
        return None

    # 2. Call Gemini API with Fallback Models
    candidate_models = [
        'models/gemini-2.0-flash',
        'models/gemini-flash-latest',
        'models/gemini-pro-latest',
        'models/gemini-2.0-flash-lite-001',
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro'
    ]
    
    response = None
    last_error = None
    
    print("  [AI] Calling Gemini API (attempting models)...")
    for model_name in candidate_models:
        try:
            print(f"  [AI] Trying model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt_text)
            print(f"  [AI] Success with model: {model_name}")
            break
        except Exception as e:
            # print(f"  [AI] Failed with {model_name}: {e}") # Reduce noise
            last_error = e
            
    if not response:
        print(f"  [AI] All models failed. Last error: {last_error}")
        return {
            "sentiment": "NEUTRAL",
            "summary": "AI 분석 불가 (API 권한 확인 필요)",
            "reasoning": f"모델 호출 실패 (404 Not Found). API Key가 'Generative Language API'를 지원하는지, 또는 해당 모델 권한이 있는지 확인해주세요. (에러: {str(last_error)})"
        }

    # 3. Parse Response
    try:
        response_text = response.text
        # Clean up code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "")
        elif response_text.startswith("```"):
             response_text = response_text.replace("```", "")
             
        result = json.loads(response_text)
        return result
        
    except Exception as e:
        print(f"  [AI] API Execution Error: {e}")
        return {
            "sentiment": "NEUTRAL",
            "summary": "AI 분석 중 오류가 발생했습니다.",
            "reasoning": str(e)
        }

def _create_prompt(data):
    """
    Helper to create a structured prompt from the data dict
    """
    
    # Extract Key Metrics safely
    kospi_close = data.get('KOSPI', {}).get('Close', 0)
    kospi_change = data.get('KOSPI', {}).get('Change_Pct', 0)
    
    kosdaq_close = data.get('KOSDAQ', {}).get('Close', 0)
    kosdaq_change = data.get('KOSDAQ', {}).get('Change_Pct', 0)
    
    sox_change = data.get('SOX', {}).get('Change_Pct', 0)
    us_bond = data.get('US10Y', {}).get('Change_Pct', 0)
    oil_change = data.get('WTI_OIL', {}).get('Change_Pct', 0)
    
    # Investor Trends (Foreigner Net)
    kospi_net_foreign = data.get('KOSPI_Net', {}).get('Foreigner', 0)
    
    # Sectors (Top movers?)
    sectors_info = ""
    if 'Sectors' in data and data['Sectors']:
        for name, info in data['Sectors'].items():
            if info:
                sectors_info += f"- {name}: {info['Change_Pct']}%\n"

    # Construct Prompt
    prompt = f"""
    You are a professional stock market analyst. Analyze the following Korean market data and provide a brief insight.

    [Market Data]
    - KOSPI: {kospi_close} ({kospi_change}%)
    - KOSDAQ: {kosdaq_close} ({kosdaq_change}%)
    - PHLX SOX: {sox_change}%
    - US 10Y Bond Yield Change: {us_bond}%
    - WTI Oil Change: {oil_change}%
    - KOSPI Foreigner Net Buy: {kospi_net_foreign} KRW
    
    [Sector Performance]
    {sectors_info}

    [Instruction]
    1. Determine the overall market sentiment (POSITIVE, NEUTRAL, NEGATIVE).
    2. Write a ONE sentence summary in Korean.
    3. Write a short reasoning (2-3 sentences) in Korean, explaining why you chose that sentiment. Focus on the relationship between SOX, Foreigner net buy, and sector movements.

    [Output Format]
    Provide ONLY a raw JSON object with no markdown formatting.
    {{
        "sentiment": "POSITIVE" | "NEUTRAL" | "NEGATIVE",
        "summary": "Korean summary here...",
        "reasoning": "Korean reasoning here..."
    }}
    """
    return prompt

if __name__ == "__main__":
    # Test Run
    sample_data = {
        "KOSPI": {"Close": 2500, "Change_Pct": 1.2},
        "KOSDAQ": {"Close": 800, "Change_Pct": -0.5},
        "SOX": {"Change_Pct": 2.5},
        "KOSPI_Net": {"Foreigner": 300000000000},
        "Sectors": {
            "Semicon": {"Change_Pct": 3.0},
            "Auto": {"Change_Pct": -1.0}
        }
    }
    print(generate_market_report(sample_data))
