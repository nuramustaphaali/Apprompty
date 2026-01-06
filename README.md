# Apprompty 🧠
> **The AI-Powered Software Architect**

Apprompty is an intelligent project planning tool that converts abstract app ideas into structured engineering blueprints. Using **DeepSeek R1 (via OpenRouter)**, it conducts a technical interview, validates requirements, and generates full system architecture, database models, and implementation tasks.

## 🚀 Features

* **Phase 1-3: Workflow Engine** - A strict state-machine that guides users from "Idea" to "Locked Requirements".
* **Phase 4: Interview Wizard** - Interactive forms to capture Intent, Tech Stack, UI/UX, and Quality requirements.
* **Phase 5: Validation Lock** - Prevents AI hallucination by freezing requirements before generation.
* **Phase 6: AI Blueprinting** - Generates a detailed JSON architecture (Frontend, Backend, API, DB) using DeepSeek.
* **Phase 7: Implementation Hub** - An interactive "To-Do" list where the AI writes the specific code for every single task.

## 🛠️ Tech Stack

* **Backend:** Python 3.10+, Django 5.x
* **Database:** SQLite3 (Dev) / PostgreSQL (Prod)
* **AI Engine:** DeepSeek R1 (Free) via OpenRouter API
* **Frontend:** Django Templates + HTMX/JS (Minimalist CSS)
* **State Management:** Custom Python State Machine (in `projects/engine.py`)

## 📦 Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/apprompty.git
    cd apprompty
    ```

2.  **Create Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```ini
    SECRET_KEY=your_django_secret_key
    DEBUG=True
    OPENROUTER_API_KEY=sk-or-v1-your-key-here
    ```

5.  **Run Migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Start Server**
    ```bash
    python manage.py runserver
    ```

Access the app at `http://127.0.0.1:8000/`.

## 🤖 AI Configuration
Apprompty uses the **OpenAI-Compatible** endpoint provided by OpenRouter.
To change the model (e.g., to Gemini or GPT-4), edit `projects/ai_service.py`:
```python
self.model = "deepseek/deepseek-r1-0528:free"
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.