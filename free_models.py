import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv('OPENROUTER_API_KEY'),
)

print("🔎 Scanning for FREE DeepSeek models...")

try:
    models = client.models.list()
    found = False
    for m in models.data:
        # Look for models with ':free' in the ID
        if ":free" in m.id and "deepseek" in m.id:
            print(f"✅ AVAILABLE FREE MODEL: {m.id}")
            found = True
            
    if not found:
        print("❌ No specific 'deepseek...:free' models found.")
        print("   Try 'google/gemini-2.0-flash-lite-preview-02-05:free' or others.")

except Exception as e:
    print(f"Connection Error: {e}")