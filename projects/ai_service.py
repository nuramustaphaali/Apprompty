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
        # UPDATED PROMPT: Richer, Professional, Specific
        system_prompt = """
        ACT AS: A Senior Principal Software Architect.
        TASK: Generate a high-fidelity technical blueprint in JSON.
        
        CRITICAL INSTRUCTIONS:
        1. CUSTOMIZATION: Use the INPUT REQUIREMENTS strictly. If they asked for "Video Streaming", include "FFmpeg" or "HLS" in the backend.
        2. SPECIFICITY: Do not say "Database". Say "PostgreSQL 16" or "MongoDB". Do not say "Auth". Say "JWT via SimpleJWT".
        3. JSON FORMAT: Output valid JSON only. No markdown.
        4. LIMITS: Max 6 items per list (to prevent timeouts). Keep descriptions professional.
        """

        user_content = f"""
        USER PROJECT REQUIREMENTS:
        {json.dumps(project_data, indent=2)}

        REQUIRED JSON OUTPUT STRUCTURE:
        {{
            "overview": "2-sentence executive technical summary.",
            "architecture": {{
                "style": "e.g. Event-Driven Microservices / Modular Monolith",
                "diagram_description": "A clear description of how data flows from user to DB."
            }},
            "frontend": {{
                "framework": "Specific Framework & Version",
                "structure": ["/src/features", "/src/shared", "/src/app"],
                "state_management": "Specific Library",
                "ui_library": "e.g. Tailwind / ShadCN / MUI"
            }},
            "backend": {{
                "framework": "Specific Framework",
                "database": "Specific Database Engine",
                "models": ["List of core domain entities (e.g. User, Subscription)"],
                "services": ["List of distinct logic layers (e.g. PaymentService, VideoTranscoder)"]
            }},
            "api": {{
                "style": "REST / GraphQL",
                "endpoints": ["List of 5 critical high-level endpoints"]
            }},
            "phases": [
                {{ "phase": 1, "title": "Foundation", "tasks": ["3 specific setup tasks"] }},
                {{ "phase": 2, "title": "Core Logic", "tasks": ["3 specific coding tasks"] }},
                {{ "phase": 3, "title": "Polish & Ship", "tasks": ["3 specific finishing tasks"] }}
            ]
        }}
        """

        try:
            # Using a slightly higher temperature for creativity, but low enough for valid JSON
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.2, 
                max_tokens=3500,
            )
            
            raw_content = response.choices[0].message.content
            clean_text = self.clean_json_string(raw_content)
            
            try:
                return json.loads(clean_text)
            except json.JSONDecodeError:
                # Fallback repair if it gets cut off
                repaired = self.repair_truncated_json(clean_text)
                return json.loads(repaired)

        except Exception as e:
            return {"error": "Blueprint Generation Failed", "raw": str(e)}
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

# projects/ai_service.py
# ... imports ...

    def generate_doc_section(self, project_context, section_key):
        """
        Generates granular, high-value documentation sections.
        """
        
        # 1. Define 8 Specialized Prompts
        prompts = {
            'overview': """
                TASK: Write the 'Executive Vision & Project Plan'.
                CONTEXT: The user wants to build a specific app described in the inputs.
                OUTPUT SECTIONS:
                - **The Core Concept**: A pitch-perfect summary of what we are building.
                - **Target Audience**: Who is this for?
                - **Success Metrics**: What defines 'done'?
                - **The "Vibe"**: Describe the feeling/experience of the app.
            """,
            'features': """
                TASK: Write the 'Platform Feature Specification'.
                CONTEXT: Based on the user's intent, list the concrete features.
                OUTPUT SECTIONS:
                - **User Stories**: "As a user, I can..." list.
                - **Core Modules**: The main functional blocks (e.g., Auth, Payments, Dashboards).
                - **Edge Cases**: Specific tricky scenarios to handle.
                - **MVP Scope**: What features are essential for version 1.0 vs later.
            """,
            'backend': """
                TASK: Write the 'Backend Architecture Strategy'.
                CONTEXT: Use the specific backend tech selected by the user (Django/Node/etc).
                OUTPUT SECTIONS:
                - **Tech Stack**: Justify the choice of framework & tools.
                - **Server Architecture**: Monolith vs Microservices decision & reasoning.
                - **Directory Structure**: ASCII tree of the backend folder.
                - **Key Libraries**: List of essential packages (e.g., DRF, Celery, Stripe).
            """,
           'database': """
                TASK: Write the 'Database Schema' as SQL Code.
                CONTEXT: The user needs to copy-paste this to create their database.
                
                CRITICAL RULE: 
                - DO NOT use text descriptions or XML. 
                - OUTPUT ONLY A VALID SQL SCRIPT inside a markdown code block.
                
                OUTPUT SECTIONS:
                1. **ER Diagram Summary** (2 sentences text).
                2. **The SQL Schema**:
                ```sql
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    ...
                );
                ```
            """,
            'frontend': """
                TASK: Write the 'Frontend Engineering Guide'.
                CONTEXT: Use the user's chosen frontend framework (React/Vue/etc).
                OUTPUT SECTIONS:
                - **Component Architecture**: How to split the UI (Atoms/Molecules).
                - **State Management**: Strategy (Redux/Zustand/Context).
                - **Routing Strategy**: List of main client-side routes.
                - **Folder Structure**: ASCII tree of the frontend `src` folder.
            """,
            'ui_ux': """
                TASK: Write the 'UI/UX & Skills.md Guide'.
                CONTEXT: Create a 'cursor rules' style guide for the AI coder.
                OUTPUT SECTIONS:
                - **Design System**: Colors, Typography, Spacing variables.
                - **Component Rules**: Rules for writing clean UI code (e.g., "Use functional components").
                - **Accessibility**: ARIA labels and contrast rules.
                - **The "Skills.md"**: A distinct block of rules to copy-paste into an AI editor.
            """,
            'api': """
                TASK: Write the 'API Specification'.
                CONTEXT: Define the communication layer.
                OUTPUT SECTIONS:
                - **Authentication Flow**: How login/token refresh works.
                - **Endpoints List**: Grouped by resource (Auth, Users, Products).
                - **Request/Response Examples**: JSON snippets for key endpoints.
                - **Error Handling**: Standard error codes (400 vs 401 vs 403).
            """,
            'setup': """
                TASK: Write the 'Master Terminal Setup Guide'.
                CONTEXT: The exact commands to boot this from zero.
                OUTPUT SECTIONS:
                - **Prerequisites**: Node/Python versions.
                - **Step 1: Backend Init**: `django-admin startproject` etc.
                - **Step 2: Frontend Init**: `npm create vite@latest` etc.
                - **Step 3: Environment**: `.env.example` file content.
                - **Step 4: Running It**: Command to start both servers.
            """
        }

        # 2. Get the specific prompt (Default to overview if missing)
        specific_instruction = prompts.get(section_key, prompts['overview'])

        system_prompt = f"""
        ACT AS: A World-Class Software Architect for "Vibecoders".
        YOUR GOAL: Create specific, actionable, high-quality documentation.
        AVOID: Generic fluff. Do not say "Use a database". Say "Use PostgreSQL because..."
        
        {specific_instruction}
        
        CRITICAL: Output valid Markdown.
        """
        
        # We include the User's specific answers to ensure it's CUSTOM
        user_content = f"""
        PROJECT CONTEXT (The User's specific answers):
        {json.dumps(project_context.get('requirements', {}), indent=2)}
        
        AI BLUEPRINT (Draft):
        {json.dumps(project_context.get('blueprint', {}), indent=2)}
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