# Apprompty 🧠
> **The AI-Powered Software Architect**

Apprompty is an intelligent project planning tool that converts abstract app ideas into structured engineering blueprints. Using **DeepSeek R1 (via OpenRouter)**, it acts as a Senior CTO, conducting a technical interview, validating requirements, and generating professional system architecture and strategic implementation guides.



[Image of software architecture diagram]


## 🚀 Features

* **Workflow Engine**
    A strict state-machine that guides users through a professional planning lifecycle, from "Raw Idea" to "Locked Requirements".

* **Interview Wizard**
    Interactive dynamic forms that capture Project Intent, Tech Stack preferences, UI/UX goals, and Quality constraints.

* **Validation Lock**
    A safety mechanism that freezes requirements before AI processing to prevent hallucinations and ensure consistency.

* **AI Blueprinting (Phase 6)**
    Generates a rigorous JSON technical blueprint covering Frontend structure, Backend models, API endpoints, and Data flow.

* **Master Documentation Hub (Phase 7)**
    A strategic "Project Bible" generator. Instead of writing snippets of code, Apprompty generates comprehensive **Strategic Guides** in a tabbed interface:
    * 📄 **Executive Summary** (Vision & Success Criteria)
    * 🛠️ **Master Setup** (Terminal commands & Environment config)
    * ⚙️ **Backend Strategy** (Schema rules & Security patterns)
    * 🎨 **Frontend Guidelines** (Component hierarchy & UX rules)
    * 🔄 **Lifecycle** (Testing & CI/CD strategies)

## 🛠️ Tech Stack

* **Backend:** Python 3.10+, Django 5.x
* **Database:** SQLite3 (Dev) / PostgreSQL (Prod)
* **AI Engine:** DeepSeek R1 (Free) via OpenRouter API
* **Frontend:** Django Templates + HTMX/JS (Minimalist CSS)
* **Architecture:** Section-Based Content Generation (to optimize token usage)

## 📦 Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/nuramustaphaali/Apprompty.git
    cd Apprompty
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

Apprompty is built to be model-agnostic using an **OpenAI-Compatible** client. By default, it uses the DeepSeek R1 Free tier via OpenRouter.

To change the model (e.g., to Gemini 2.0 or GPT-4), edit `projects/ai_service.py`:

```python
# projects/ai_service.py
self.model = "deepseek/deepseek-r1-0528:free" 
# Or change to: "google/gemini-2.0-flash-001"

```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
