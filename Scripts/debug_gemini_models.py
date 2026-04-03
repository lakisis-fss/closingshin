
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("API Key not found.")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    try:
        print("Listing available models to models_list.txt...")
        with open("models_list.txt", "w", encoding="utf-8") as f:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    f.write(f"{m.name}\n")
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
