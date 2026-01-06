# Contributing to Apprompty

First off, thanks for taking the time to contribute! 🎉

## How to Contribute

1.  **Fork the repository** on GitHub.
2.  **Clone the project** to your own machine.
3.  **Create a branch** for your feature or bug fix:
    ```bash
    git checkout -b feature/amazing-feature
    ```
4.  **Commit changes** to your own branch.
5.  **Push** your work back up to your fork.
6.  Submit a **Pull Request** so we can review your changes.

## Development Guidelines

* **Code Style:** We follow PEP 8 for Python code.
* **AI Prompts:** All prompt engineering logic resides in `projects/ai_service.py`. Do not hardcode prompts in views.
* **State Machine:** Any changes to the project flow (Phases 1-7) must be updated in `projects/engine.py` and `projects/constants.py`.

## Reporting Bugs

Please use the GitHub Issues tab to report bugs. Include your Python version and the specific error message (e.g., specific JSON parsing errors from the AI).