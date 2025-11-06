# Sports Chatbot — Local dev

Quick steps to get the backend and frontend running locally on Windows (PowerShell).

Prereqs
- Python 3.8+ installed
- Git (optional)

1) Create & activate venv, install deps

```powershell
cd D:\sports-chatbot
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2) Provide secrets
- Copy `.env.example` to `.env` and add your `OPENROUTER_API_KEY` if you want LLM fallback.

3) Seed the database

```powershell
python backend\setup_db.py
```

4) Start the backend

```powershell
python backend\app.py
# or (recommended) open a new terminal and run the command above
```

5) Serve the frontend (so browser origin is http://)

```powershell
# from repo root
python -m http.server 8000 -d frontend
# open http://127.0.0.1:8000/index.html
```

6) Tests

- Health: http://127.0.0.1:5000/health
- LLM test (requires API key): http://127.0.0.1:5000/llm_test
- Chat endpoint (POST): http://127.0.0.1:5000/chat

Troubleshooting
- If the server prints it's running but you can't connect, check firewall and that no other process uses the port. Use `netstat -ano | findstr 5000`.
