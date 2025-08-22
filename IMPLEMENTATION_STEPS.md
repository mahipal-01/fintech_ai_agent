IMPLEMENTATION STEPS - Perplexity + Local Embeddings + Google Sheets Escalation

1) Create & activate a Python virtual environment
   python -m venv venv
   # Windows (cmd): venv\Scripts\activate
   # PowerShell: venv\Scripts\Activate.ps1 (may need Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)
   # mac/linux: source venv/bin/activate

2) Install dependencies
   pip install -r requirements.txt

3) Place your Google service account JSON in the project root (optional)
   - If using service account logging, save the JSON as 'service_account.json' or update .env SERVICE_ACCOUNT_FILE

4) Put your FAQ files into data/ (faqs.txt is included as example)

5) Build vectorstore (local embeddings)
   python rag_build.py

6) Run the app
   uvicorn app:app --reload

7) Open http://127.0.0.1:8000 and test
   - Enter name & email (optional)
   - Ask a question. If you type 'I want to talk to a human' or similar, it will be logged to Google Sheets.

Notes:
- If PERPLEXITY_API_KEY is set, the app calls Perplexity's chat completions endpoint for LLM answers.
- If PERPLEXITY_API_KEY is not set, the app will attempt to call a local Ollama model (llama3.1:8b).
- You can also set APPS_SCRIPT_WEBHOOK_URL to have the server POST escalations to a Google Apps Script web app.