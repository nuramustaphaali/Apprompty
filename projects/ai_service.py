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
        """
        Aggressively cleans the AI output to extract just the JSON.
        """
        # 1. Remove <think> blocks (Reasoning trace)
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        
        # 2. Remove markdown code wrappers
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'```$', '', text, flags=re.MULTILINE)
        
        return text.strip()

    def repair_truncated_json(self, json_str):
        """
        Attempts to fix JSON that was cut off mid-stream.
        This is critical for free-tier models with low token limits.
        """
        json_str = json_str.strip()
        
        # Simple heuristic: Balance braces/brackets
        open_braces = json_str.count('{') - json_str.count('}')
        open_brackets = json_str.count('[') - json_str.count(']')
        
        # Append missing closing characters
        # We generally close lists first, then objects
        json_str += ']' * open_brackets
        json_str += '}' * open_braces
        
        return json_str

    def generate_blueprint(self, project_data):
        # UPDATED PROMPT: Strict limits to prevent cutoff
        system_prompt = """
        ACT AS: A Senior Software Architect.
        TASK: Generate a technical blueprint in JSON.
        
        CRITICAL TOKEN LIMIT RULES:
        1. OUTPUT MUST BE VALID JSON ONLY.
        2. NO conversational text.
        3. LIST LIMIT: Max 3 items per list (e.g., 3 tasks, 3 models).
        4. BREVITY: Keep descriptions under 10 words.
        5. All keys must be lowercase.
        """

        user_content = f"""
        INPUT REQUIREMENTS:
        {json.dumps(project_data, indent=2)}

        REQUIRED JSON STRUCTURE:
        {{
            "overview": "Short summary...",
            "architecture": {{
                "style": "Monolithic/Microservices",
                "diagram_description": "Brief flow description"
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
                "endpoints": ["GET /api/users"]
            }},
            "ui_ux": {{
                "theme": "Dark/Light",
                "components": ["Navbar", "Sidebar"]
            }},
            "phases": [
                {{ "phase": 1, "title": "Setup", "tasks": ["Init Repo", "Config DB"] }}
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
                max_tokens=3000, # Increased limit
            )
            
            raw_content = response.choices[0].message.content
            clean_text = self.clean_json_string(raw_content)
            
            try:
                # Attempt 1: Parse directly
                return json.loads(clean_text)
            except json.JSONDecodeError:
                # Attempt 2: Repair truncated JSON
                print("⚠️ JSON Truncated. Attempting repair...")
                repaired_text = self.repair_truncated_json(clean_text)
                try:
                    return json.loads(repaired_text)
                except:
                    # Final Fallback
                    return {"error": "JSON Cutoff", "raw": raw_content}

        except Exception as e:
            return {"error": "Service Failed", "raw": str(e)}

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
                temperature=0.3,
            )
            return response.choices[0].message.content
            
        except Exception as e:
            return f"AI Error: {str(e)}"

    def generate_project_docs(self, project_context):
        """
        Generates a Strategic Project Guide (Stored in DB).
        """
        system_prompt = """
        ACT AS: A Senior CTO and Product Manager.
        TASK: Write a comprehensive Strategic Master Plan and Setup Guide.
        
        CRITICAL RULES:
        1. DO NOT WRITE CODE. (No Python classes, no React components, no function bodies).
        2. FOCUS ON: Architecture, Data Strategy, UI/UX Guidelines, and Best Practices.
        3. PROVIDE: "Terminal Commands" only for project initialization (pip install, etc).
        4. TONE: Professional, guiding, authoritative.
        """
        
        user_content = f"""
        PROJECT BLUEPRINT:
        {json.dumps(project_context, indent=2)}
        
        Please generate a master markdown document with these exact sections:

        # 1. Executive Summary
        - Project Vision & Success Criteria.
        - The "Why" behind the architecture choices.

        # 2. Master Setup Guide (Terminal Only)
        - Step-by-step shell commands to initialize this specific tech stack.
        - Dependency installation guide.

        # 3. Backend Strategy (Conceptual)
        - Database Schema Rules (Explain relationships, don't write SQL).
        - API Design Patterns (REST vs GraphQL strategy).
        - Security & Scalability requirements.

        # 4. Frontend & UI/UX Guidelines
        - Component Hierarchy (Explain the folder structure).
        - State Management Strategy (When to use Redux/Context).
        - UI Polishing Guide (Typography, Spacing, Accessibility rules).

        # 5. The "Phase 8" (Post-Setup Lifecycle)
        - Testing Strategy (What to test and how).
        - Deployment Pipeline (CI/CD recommendations).
        - Maintenance Checklist (Logging, Monitoring).
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
            return self.clean_json_string(response.choices[0].message.content)
            
        except Exception as e:
            return f"Documentation Error: {str(e)}"

# ... imports ...

    def generate_doc_section(self, project_context, section_key):
        """
        Generates ONE specific section of the documentation to save tokens.
        """
        
        # 1. Define Prompts for each Section
        prompts = {
            'intro': """
                TASK: Write the 'Executive Summary' and 'Vision'.
                CONTENT:
                - Project Title & High-level purpose.
                - The "Why": Business value and problem solved.
                - Success Criteria: How do we know it works?
                - NO CODE. Markdown format.
            """,
            'setup': """
                TASK: Write the 'Master Setup Guide'.
                CONTENT:
                - Prerequisites (Node, Python, Docker versions).
                - Terminal Commands for initialization (git init, pip install, etc).
                - Environment Variable setup (.env example).
                - NO Application Code (No views/models), ONLY Setup commands.
            """,
            'backend': """
                TASK: Write the 'Backend Strategy'.
                CONTENT:
                - Database Table Dat NOT Schema Description (Relationships, key fields) keep it short.
                - API Architecture (REST/GraphQL endpoints logic) keep it short nut full.
                - Authentication Strategy (JWT, OAuth details) short.
                - Security measures, very consise.
            """,
            'frontend': """
                TASK: Write the 'Frontend & UI Guidelines'.
                CONTENT:
                - Component Hierarchy (Folder structure explanation).
                - State Management Strategy.
                - UI/UX Rules (Color usage, Typography, Accessibility).
                - Critical Libraries list.
            """,
            'lifecycle': """
                TASK: Write the 'Phase 8: Lifecycle'.
                CONTENT:
                - Testing Strategy (Unit vs E2E).
                - Deployment Pipeline (CI/CD suggestions).
                - Maintenance (Logging, Monitoring).
                - Future Roadmap suggestions.
            """
        }

        # 2. Get the specific prompt
        specific_instruction = prompts.get(section_key, prompts['intro'])

        system_prompt = f"""
        ACT AS: A Senior CTO.
        {specific_instruction}
        
        CRITICAL: Output valid Markdown. Be professional and strategic.
        """
        
        user_content = f"""
        PROJECT BLUEPRINT:
        {json.dumps(project_context, indent=2)}
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
            return self.clean_json_string(response.choices[0].message.content)
            
        except Exception as e:
            return f"Error generating section: {str(e)}"