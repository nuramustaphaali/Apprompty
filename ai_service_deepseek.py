"""
=============================================================================
🔹 CONFIGURATION INSTRUCTIONS (Read First)
=============================================================================

1. GET API KEY:
   - Go to: https://platform.deepseek.com/api_keys
   - Create a new API Key (starts with 'sk-...')
   - Add credit to your account ($5-10 is plenty).

2. UPDATE .env FILE:
   Add this line to your .env file:
   DEEPSEEK_API_KEY=sk-your-actual-api-key-here

3. UPDATE config/settings.py:
   Add this line to your settings.py file:
   DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

=============================================================================
"""

from openai import OpenAI
from django.conf import settings
import json
import re

class AIService:
    def __init__(self):
        # 1. Initialize Client pointing strictly to DeepSeek Official API
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        # 2. Define the Model
        # 'deepseek-chat' (V3) is cheaper and faster.
        # 'deepseek-reasoner' (R1) is smarter for complex architecture.
        self.model = "deepseek-reasoner" 

    def clean_json_string(self, text):
        """
        Cleans AI output to extract pure JSON.
        Removes <think> blocks (reasoning trace) and markdown wrappers.
        """
        # 1. Remove <think>...</think> blocks (Specific to DeepSeek R1)
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        
        # 2. Remove markdown code wrappers
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'```$', '', text, flags=re.MULTILINE)
        
        return text.strip()

    def repair_truncated_json(self, json_str):
        """
        Attempts to fix JSON that was cut off mid-stream.
        """
        json_str = json_str.strip()
        open_braces = json_str.count('{') - json_str.count('}')
        open_brackets = json_str.count('[') - json_str.count(']')
        json_str += ']' * open_brackets
        json_str += '}' * open_braces
        return json_str

    def generate_blueprint(self, project_data):
        system_prompt = """
        ACT AS: A Senior CTO & Software Architect.
        TASK: Generate a production-grade technical blueprint in JSON.
        
        CRITICAL RULES:
        1. OUTPUT MUST BE VALID JSON ONLY.
        2. NO conversational text or preambles.
        3. LIST LIMIT: Max 5 items per list to ensure depth without timeouts.
        4. All keys must be lowercase.
        """

        user_content = f"""
        INPUT REQUIREMENTS:
        {json.dumps(project_data, indent=2)}

        REQUIRED JSON STRUCTURE:
        {{
            "overview": "Detailed executive summary (2-3 sentences)...",
            "architecture": {{
                "style": "e.g., Modular Monolith / Microservices",
                "diagram_description": "Detailed data flow description..."
            }},
            "frontend": {{
                "framework": "Specific Framework & Version",
                "structure": ["/src/components", "/src/hooks", "/src/pages", "/src/utils"],
                "state_management": "Specific library recommendation"
            }},
            "backend": {{
                "framework": "Specific Framework",
                "database": "PostgreSQL / SQLite config",
                "models": ["User", "Order", "Product", "Payment"],
                "services": ["AuthService", "PaymentService", "EmailService"]
            }},
            "api": {{
                "style": "REST / GraphQL",
                "endpoints": ["GET /api/v1/users/me", "POST /api/v1/orders", "PUT /api/v1/products/:id"]
            }},
            "ui_ux": {{
                "theme": "Color palette & Typography",
                "components": ["DashboardLayout", "DataGrid", "AuthForm", "Modal"]
            }},
            "phases": [
                {{ 
                    "phase": 1, 
                    "title": "Initialization", 
                    "tasks": ["Set up Git repo", "Initialize Django Project", "Configure Docker"] 
                }},
                {{
                    "phase": 2,
                    "title": "Core Features",
                    "tasks": ["Implement User Model", "Set up Authentication API"]
                }}
            ]
        }}
        """

        try:
            # Note: DeepSeek Reasoner does NOT support 'system' role in some versions.
            # We put everything in 'user' role just to be safe, or use standard 'system'.
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.0, # Zero temp for strict JSON
                max_tokens=4000, # Paid version allows more tokens
            )
            
            raw_content = response.choices[0].message.content
            clean_text = self.clean_json_string(raw_content)
            
            try:
                return json.loads(clean_text)
            except json.JSONDecodeError:
                repaired_text = self.repair_truncated_json(clean_text)
                return json.loads(repaired_text)

        except Exception as e:
            return {"error": "DeepSeek Service Failed", "raw": str(e)}

    def generate_task_guide(self, project_context, current_task):
        system_prompt = """
        ACT AS: A Senior Lead Developer.
        TASK: Write a step-by-step implementation guide.
        CONTEXT: Extremely explicit code for a Junior Developer.
        
        OUTPUT FORMAT (Markdown):
        ## Goal
        1-sentence summary.
        
        ### 1. Terminal
        `pip install ...`
        
        ### 2. Code
        **File: path/to/file.py**
        ```python
        # Code here
        ```
        """
        
        user_content = f"""
        CONTEXT: {json.dumps(project_context)}
        TASK: "{current_task}"
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.2,
            )
            return response.choices[0].message.content
            
        except Exception as e:
            return f"AI Error: {str(e)}"