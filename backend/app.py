from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, re, joblib, os, requests
from contextlib import closing
from random import choice
from dotenv import load_dotenv

# --- CONFIG ---
DB_PATH = "backend/db.sqlite3"
MODEL_PATH = "nlp/artifacts/intent_model.pkl"
CONF_THRESHOLD = 0.4  # below this, we fall back to LLM
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# OpenRouter model to use for LLM fallback (user requested)
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "tngtech/deepseek-r1t2-chimera:free")

# load secrets
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)
CORS(app)

# --- INTENT MODEL ---
intent_model = joblib.load(MODEL_PATH)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_teams(conn):
    q = "SELECT DISTINCT home_team FROM matches UNION SELECT DISTINCT away_team FROM matches"
    return [r[0] for r in conn.execute(q).fetchall()]

def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()

def extract_teams_from_text(text: str, teams):
    text_n = normalize(text)
    found = []
    for t in sorted(teams, key=lambda x: -len(x)):
        if normalize(t) in text_n and t not in found:
            found.append(t)
        if len(found) == 2:
            break
    if len(found) < 2:
        m = re.search(r"(.+?)\s+vs\s+(.+)", text, flags=re.I)
        if m: return m.group(1).strip(), m.group(2).strip()
    return (found[0], found[1]) if len(found) == 2 else (None, None)

def find_match_row(conn, team_a, team_b):
    q = """
    SELECT * FROM matches
    WHERE (LOWER(home_team) = LOWER(?) AND LOWER(away_team) = LOWER(?))
       OR (LOWER(home_team) = LOWER(?) AND LOWER(away_team) = LOWER(?))
    LIMIT 1
    """
    with closing(conn.cursor()) as cur:
        cur.execute(q, (team_a, team_b, team_b, team_a))
        return cur.fetchone()

def intent_with_conf(text: str):
    # predict intent + probability for thresholding
    probs = intent_model.predict_proba([text])[0]
    label = intent_model.classes_[probs.argmax()]
    conf = float(probs.max())
    return label, conf

def llm_reply(history, sys_prompt="You are a friendly sports assistant. Keep replies concise. If user asks about our demo teams (Alpha FC, Beta United, etc.), answer naturally using generic phrasing. If you don't know, say so briefly."):
    if not OPENROUTER_API_KEY:
        return "LLM not configured. Ask about score, stadium, scorers, date or tournament for our demo matches."
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        # Use model configured by OPENROUTER_MODEL (defaults to tngtech/deepseek-r1t2-chimera:free)
        "model": OPENROUTER_MODEL,
        "messages": [{"role":"system","content":sys_prompt}] + history,
        "max_tokens": 180,
        "temperature": 0.7
    }
    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=25)
        r.raise_for_status()
        data = r.json()
        reply = data["choices"][0]["message"]["content"].strip()
        # Handle empty responses from free models
        if not reply:
            return "I understand your question, but I'm not sure how to respond right now. Try asking about specific match details!"
        return reply
    except Exception as e:
        return "Sorry, I couldn't think of a good answer right now."


@app.get("/llm_test")
def llm_test():
    """Lightweight test to verify OpenRouter connectivity and model selection.

    Returns a short reply from the configured model (truncated) or an error.
    This endpoint will NOT return the API key. It requires the local .env to have OPENROUTER_API_KEY set.
    """
    if not OPENROUTER_API_KEY:
        return jsonify({"ok": False, "error": "OPENROUTER_API_KEY not set locally"}), 400

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    test_prompt = "Please reply with a very short yes/no acknowledgement so we can test connectivity."
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "system", "content": "Connectivity test"}, {"role": "user", "content": test_prompt}],
        "max_tokens": 16,
        "temperature": 0.0,
    }
    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=12)
        r.raise_for_status()
        data = r.json()
        # Try to extract a short text reply safely
        reply = None
        try:
            reply = data["choices"][0]["message"]["content"].strip()
        except Exception:
            # Fallback to raw repr (not including API key)
            reply = str(data)[:250]

        return jsonify({"ok": True, "model": OPENROUTER_MODEL, "reply": reply})
    except requests.exceptions.RequestException as e:
        return jsonify({"ok": False, "error": "Request failed", "detail": str(e)}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": "Unexpected error", "detail": str(e)}), 500

@app.get("/")
def index():
    return (
        "<h3>Sports Chatbot API</h3>"
        "<p>Try: /health (GET), /ask (POST: legacy), /chat (POST: conversational)</p>"
    )

@app.get("/health")
def health():
    return {"status": "ok"}

# Legacy structured endpoint (kept)
@app.post("/ask")
def ask():
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"answer": "Please provide a message."}), 400

    intent, _ = intent_with_conf(message)
    conn = get_conn()
    teams = get_all_teams(conn)
    team_a, team_b = extract_teams_from_text(message, teams)
    if not team_a or not team_b:
        return jsonify({"intent": intent, "answer": "Please mention two teams (e.g., 'Alpha FC vs Beta United')."})
    row = find_match_row(conn, team_a, team_b)
    if not row:
        return jsonify({"intent": intent, "answer": f"No match found for '{team_a} vs {team_b}' in the dummy data."})

    if intent == "score":
        answer = f"{row['home_team']} {row['home_score']} - {row['away_score']} {row['away_team']} (Tournament: {row['tournament'] or '—'}, Stadium: {row['stadium'] or '—'}, Date: {row['date'] or '—'})"
    elif intent == "stadium":
        answer = f"Stadium: {row['stadium'] or '—'} (Date: {row['date'] or '—'})"
    elif intent == "scorers":
        with closing(conn.cursor()) as cur:
            cur.execute("SELECT player_name, team FROM scorers WHERE match_id = ?", (row["match_id"],))
            sc = cur.fetchall()
        answer = "No scorers recorded for this match." if not sc else "Scorers: " + ", ".join(f"{r['player_name']} ({r['team'] or '—'})" for r in sc)
    elif intent == "date":
        answer = f"Match date: {row['date'] or '—'}"
    elif intent == "tournament":
        answer = f"Tournament: {row['tournament'] or '—'}"
    else:
        answer = "I can help with score, stadium, scorers, date, or tournament."
    return jsonify({"intent": intent, "answer": answer})

# New conversational endpoint with fallback
@app.post("/chat")
def chat():
    """
    Request JSON:
    {
      "message": "free text",
      "history": [{"role":"user","content":"..."},{"role":"assistant","content":"..."}]
    }
    """
    payload = request.get_json(force=True) or {}
    message = (payload.get("message") or "").strip()
    history = payload.get("history") or []
    if not message:
        return jsonify({"answer": "Say something to start!"}), 400

    # 1) Try structured answer if confident AND two teams found
    intent, conf = intent_with_conf(message)
    conn = get_conn()
    teams = get_all_teams(conn)
    team_a, team_b = extract_teams_from_text(message, teams)
    row = None
    
    if conf >= CONF_THRESHOLD and team_a and team_b:
        row = find_match_row(conn, team_a, team_b)

    if row:
        if intent == "score":
            answer = f"{row['home_team']} {row['home_score']}-{row['away_score']} {row['away_team']}."
        elif intent == "stadium":
            answer = f"The game was at {row['stadium'] or '—'}."
        elif intent == "scorers":
            with closing(conn.cursor()) as cur:
                cur.execute("SELECT player_name, team FROM scorers WHERE match_id = ?", (row["match_id"],))
                sc = cur.fetchall()
                answer = "No scorers recorded." if not sc else "Scorers: " + ", ".join(f"{r['player_name']} ({r['team'] or '—'})" for r in sc)
        elif intent == "date":
            answer = f"They played on {row['date'] or '—'}."
        elif intent == "tournament":
            answer = f"It was part of the {row['tournament'] or '—'}."
        else:
            answer = "I can help with score, stadium, scorers, date, or tournament."
        # make it conversational
        answer = f"{answer} Anything else you want to check?"
        return jsonify({"intent": intent, "confidence": conf, "answer": answer})

    # 2) Fall back to LLM for small-talk or low confidence
    llm_history = history + [{"role":"user","content": message}]
    answer = llm_reply(llm_history)
    return jsonify({"intent": "chitchat", "confidence": conf, "answer": answer})


if __name__ == "__main__":
    # Allow running the app directly for local testing: `python backend/app.py`
    port = int(os.environ.get("PORT", 5000))
    # Respect FLASK_DEBUG env var; default to False so the development reloader
    # doesn't spawn a child process (makes background runs simpler).
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
