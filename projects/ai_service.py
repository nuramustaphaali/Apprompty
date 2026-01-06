from openai import OpenAI
from django.conf import settings
import json
import re

class AIService:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
            default_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Apprompty",
            }
        )
        self.model = "deepseek/deepseek-r1-0528:free" 

    def clean_json_string(self, text):
        # 1. Remove <think> blocks
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # 2. Remove markdown
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'```$', '', text, flags=re.MULTILINE)
        return text.strip()

    def generate_blueprint(self, project_data):
        # UPDATED PROMPT: Enforces brevity to prevent "Unterminated String" errors
        system_prompt = """
        ACT AS: A Senior Software Architect.
        TASK: Generate a technical blueprint in JSON.
        
        CRITICAL RULES:
        1. OUTPUT MUST BE VALID JSON ONLY.
        2. NO conversational text.
        3. KEEP DESCRIPTIONS CONCISE (Max 2 sentences per field) to avoid token limits.
        4. All keys must be lowercase.
        """

        user_content = f"""
        INPUT REQUIREMENTS:
        {json.dumps(project_data, indent=2)}

        REQUIRED JSON STRUCTURE:
        {{
            "overview": "Short summary (max 50 words)...",
            "architecture": {{
                "style": "Monolithic/Microservices",
                "diagram_description": "Brief data flow description"
            }},
            "frontend": {{
                "framework": "React/Vue/etc",
                "structure": ["/src", "/components", "/assets"],
                "state_management": "Redux/Context"
            }},
            "backend": {{
                "framework": "Django/Node",
                "models": ["User", "Order", "Product"],
                "services": ["AuthService", "DataService"]
            }},
            "api": {{
                "endpoints": ["GET /api/users", "POST /api/orders"]
            }},
            "ui_ux": {{
                "theme": "Dark/Light",
                "components": ["Navbar", "Footer", "Card"]
            }},
            "phases": [
                {{ "phase": 1, "title": "Setup", "tasks": ["Init Repo", "Config DB"] }},
                {{ "phase": 2, "title": "MVP", "tasks": ["User Auth", "Core Feature"] }}
            ]
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.3,
                max_tokens=2000, # Ensure enough room for completion
            )
            
            raw_content = response.choices[0].message.content
            clean_text = self.clean_json_string(raw_content)
            return json.loads(clean_text)

        except json.JSONDecodeError:
            print(f"❌ JSON Cutoff Error. Raw tail: {raw_content[-100:]}")
            return {"error": "AI response was truncated. Please try again.", "raw": raw_content}
        except Exception as e:
            return {"error": "Service Failed", "raw": str(e)}
            
    def generate_task_guide(self, project_context, current_task):
        """
        Generates detailed coding steps for Phase 7 (Implementation Hub).
        """
        system_prompt = """
        ACT AS: A Senior Lead Developer.
        TASK: Write a step-by-step implementation guide for a specific task.
        CONTEXT: You are writing this for a Junior Developer. Be extremely explicit.
        
        OUTPUT FORMAT (Markdown):
        ## Goal
        1-sentence summary.
        
        ### 1. Terminal Commands
        `pip install ...` or `npm install ...`
        
        ### 2. Code Changes
        **File: path/to/file.py**
        ```python
        # The exact code to write
        ```
        
        ### 3. Verification
        How to check if it works.
        """
        
        user_content = f"""
        PROJECT CONTEXT:
        Frontend: {project_context.get('frontend', {}).get('framework')}
        Backend: {project_context.get('backend', {}).get('framework')}
        Database: {project_context.get('backend', {}).get('database')}
        
        CURRENT TASK:
        "{current_task}"
        
        Provide the complete code and commands to implement this task.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.3,
            )
            return response.choices[0].message.content
            
        except Exception as e:
            return f"AI Error: {str(e)}"