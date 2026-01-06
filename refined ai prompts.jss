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
        # Using the DeepSeek R1 Free model
        self.model = "deepseek/deepseek-r1-0528:free" 

    def clean_json_string(self, text):
        """
        Removes <think> blocks and markdown wrappers to get pure JSON.
        """
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'```$', '', text, flags=re.MULTILINE)
        return text.strip()

    def generate_blueprint(self, project_data):
        system_prompt = """
        ACT AS: A CTO & Senior Software Architect.
        TASK: Create a comprehensive, production-grade technical blueprint.
        
        CRITICAL RULES:
        1. OUTPUT MUST BE VALID JSON ONLY. NO MARKDOWN.
        2. NO conversational text or thinking logs.
        3. All keys must be lowercase.
        4. BE SPECIFIC: Do not just say "Auth", say "JWT via SimpleJWT".
        """

        user_content = f"""
        INPUT REQUIREMENTS:
        {json.dumps(project_data, indent=2)}

        REQUIRED JSON STRUCTURE:
        {{
            "overview": "Detailed executive summary...",
            "architecture": {{
                "style": "e.g., Modular Monolith / Microservices",
                "diagram_description": "Step-by-step data flow description..."
            }},
            "frontend": {{
                "framework": "Specific Framework & Version",
                "structure": ["/src/components", "/src/hooks", "/src/pages"],
                "state_management": "Specific library recommendation",
                "key_libraries": ["List of critical libraries needed"]
            }},
            "backend": {{
                "framework": "Specific Framework",
                "database": "PostgreSQL / SQLite config",
                "models": ["User (fields: email, password, role)", "Order (fields: total, date)"],
                "services": ["AuthService", "PaymentService", "EmailService"]
            }},
            "api": {{
                "style": "REST / GraphQL",
                "endpoints": ["GET /api/v1/users/me", "POST /api/v1/orders"]
            }},
            "ui_ux": {{
                "theme": "Color palette & Typography",
                "components": ["DashboardLayout", "DataGrid", "AuthForm"]
            }},
            "phases": [
                {{ 
                    "phase": 1, 
                    "title": "Project Initialization", 
                    "tasks": ["Set up Git repo", "Initialize Django Project", "Configure Docker"] 
                }},
                {{
                    "phase": 2,
                    "title": "Core Architecture",
                    "tasks": ["Implement User Model", "Set up Authentication API"]
                }}
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
                temperature=0.2,
            )
            raw_content = response.choices[0].message.content
            clean_text = self.clean_json_string(raw_content)
            return json.loads(clean_text)

        except Exception as e:
            print(f"❌ Blueprint Generation Error: {e}")
            return {"error": "Generation Failed", "raw": str(e)}

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