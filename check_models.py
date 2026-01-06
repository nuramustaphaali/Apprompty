import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv('OPENROUTER_API_KEY')

print(f"🔎 DEBUG: Loaded OpenRouter Key: ...{api_key[-4:] if api_key else 'NONE'}")

if not api_key:
    print("❌ ERROR: No OPENROUTER_API_KEY found in .env file.")
    exit()

# 2. Configure Client for OpenRouter
client = OpenAI(
    base_url="[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)",
    api_key=api_key,
)

print(f"📡 CONNECTING TO: [https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)")

try:
    # 3. List Models
    models = client.models.list()
    
    print("\n✅ SUCCESS! OpenRouter Connected.")
    print("   Here are the available DeepSeek models:\n")
    
    found_any = False
    for model in models.data:
        # Filter just to show deepseek related ones to keep list clean
        if "deepseek" in model.id.lower():
            print(f"   - {model.id}")
            found_any = True
            
    if not found_any:
        print("   (No specific 'deepseek' named models found, but connection is good!)")

except Exception as e:
    print("\n❌ CONNECTION FAILED")
    print(f"Error: {e}")