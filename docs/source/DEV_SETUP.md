# 🛠 Development Setup

This project uses **Python 3.12+**. Follow these instructions to set up your development environment.

---

## Prerequisites

1. Install **Python 3.12 or higher**.
   - On Ubuntu/Debian:
     ```bash
     sudo apt update
     sudo apt install python3.12 python3.12-venv python3.12-dev
     ```
   - On macOS (using Homebrew):
     ```bash
     brew install python@3.12
     ```

2. Ensure `pip` is up-to-date:
   ```bash
   python3 -m pip install --upgrade pip

## Setup Virtual Environment

This project adheres to PEP 668 (system Python is externally managed). Always use a virtual environment to avoid conflicts with system packages.

1. Create a virtual environment:

  `python3 -m venv .venv`

2. Ensure `pip` is up-to-date:

  - On Ubuntu/macOS:
    ```bash
    source .venv/bin/activate
    ```
  - On Windows (PowerShell):
    ```bash
    .\.venv\Scripts\Activate.ps1
    ```

3. Install the project in editable mode:
   ```bash
   pip install -e .
   ```

## Troubleshooting

  - If you encounter issues with dependencies, try:

    ```bash
    pip install --force-reinstall -e .
    ```
  - If the virtual environment is corrupted, delete the .venv directory and recreate it:
    ```bash
    rm -rf .venv
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .
    ```

## Docker Development (Optional)

If you prefer using Docker for development, see the Docker Setup Guide.


