from openai import OpenAI
from django.conf import settings
import json
import re

class AIService:
    def __init__(self):
        # Initialize OpenRouter Client
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
            default_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Apprompty",
            }
        )
        
        # ✅ SELECTED FREE MODEL
        self.model = "deepseek/deepseek-r1-0528:free" 

    def clean_json_string(self, text):
        """
        DeepSeek R1 often 'thinks' out loud before answering.
        We must remove the <think> block and any markdown to get pure JSON.
        """
        # 1. Remove <think>...</think> blocks (Reasoning trace)
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        
        # 2. Remove markdown code wrappers (```json ... ```)
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'```$', '', text, flags=re.MULTILINE)
        
        # 3. Trim extra whitespace
        return text.strip()

    def generate_blueprint(self, project_data):
        # Prompt engineered for R1 (Reasoning models prefer clear goals)
        system_prompt = """
        ACT AS: A Senior Software Architect.
        TASK: Generate a complete technical blueprint in JSON format.
        
        CRITICAL RULES:
        1. OUTPUT MUST BE VALID JSON ONLY.
        2. DO NOT include "Here is the JSON" or conversational filler.
        3. DO NOT output the <think> process in the final response if possible.
        4. All JSON keys must be lowercase.
        """

        user_content = f"""
        INPUT REQUIREMENTS:
        {json.dumps(project_data, indent=2)}

        REQUIRED JSON STRUCTURE:
        {{
            "overview": "High-level summary...",
            "architecture": {{
                "style": "Monolithic/Microservices",
                "diagram_description": "Description of data flow"
            }},
            "frontend": {{
                "framework": "React/Vue/etc",
                "structure": ["/src", "/components"],
                "state_management": "Redux/Context"
            }},
            "backend": {{
                "framework": "Django/Node",
                "models": ["User", "Order"],
                "services": ["AuthService"]
            }},
            "api": {{
                "endpoints": ["GET /api/v1/users"]
            }},
            "ui_ux": {{
                "theme": "Dark/Light",
                "components": ["Navbar", "Sidebar"]
            }},
            "phases": [
                {{ "phase": 1, "title": "Setup", "tasks": ["Task 1"] }}
            ]
        }}
        """

        try:
            # Call OpenRouter API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.3, # Low temperature keeps JSON stable
            )

            raw_content = response.choices[0].message.content
            
            # Clean and Parse
            clean_text = self.clean_json_string(raw_content)
            data = json.loads(clean_text)
            
            return data

        except json.JSONDecodeError:
            print("❌ JSON Parsing Error. Content was:", raw_content)
            return {
                "overview": "Error: AI generated invalid JSON.",
                "architecture": {"style": "Error", "diagram_description": "Raw Output: " + str(raw_content[:200])},
                "backend": {"models": [], "services": []},
                "api": {"endpoints": []},
                "phases": []
            }
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return {"error": "OpenRouter Service Failed", "raw": str(e)}