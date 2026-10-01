import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def call_gemini(prompt, model="gemini-3.8-flash", max_retries=5):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            if "503" in str(e) and attempt < max_retries - 1:
                wait = 5 * (attempt + 1)  # 5s, 10s, 15s, 20s...
                print(f"  Model busy, retrying in {wait}s (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
            else:
                raise

result = call_gemini("Say hello in one sentence.")
print(result)