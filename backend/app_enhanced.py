# Enhanced Backend with New Intents and Optimizations
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, re, joblib, os, requests
from contextlib import closing
from random import choice
from dotenv import load_dotenv
from functools import lru_cache
import json
from datetime import datetime

# --- CONFIG ---
DB_PATH = "db.sqlite3"
MODEL_PATH = "../nlp/artifacts/intent_model_enhanced.pkl"
CONF_THRESHOLD = 0.6  # Updated based on enhanced model analysis
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "tngtech/deepseek-r1t2-chimera:free")

# load secrets
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)
CORS(app)

# --- ENHANCED INTENT MODEL ---
try:
    intent_model = joblib.load(MODEL_PATH)
    print("✅ Enhanced intent model loaded successfully")
except Exception as e:
    print(f"⚠️ Could not load enhanced model, falling back to original: {e}")
    try:
        intent_model = joblib.load("../nlp/artifacts/intent_model.pkl")
        print("✅ Fallback model loaded")
    except:
        print("❌ No model found!")
        intent_model = None

@lru_cache(maxsize=128)
def get_conn():
    """Cached database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def intent_with_conf(text):
    """Get intent prediction with confidence score"""
    if not intent_model:
        return None, 0.0
    
    try:
        proba = intent_model.predict_proba([text])[0]
        intent = intent_model.classes_[proba.argmax()]
        confidence = proba.max()
        print(f"🧠 Intent: {intent}, Confidence: {confidence:.3f}")
        return intent, confidence
    except Exception as e:
        print(f"Intent prediction error: {e}")
        return None, 0.0

@lru_cache(maxsize=64)
def extract_teams_from_text(text):
    """Enhanced team extraction with caching"""
    teams = []
    with closing(get_conn()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM teams")
        all_teams = [row[0] for row in cursor.fetchall()]
    
    text_lower = text.lower()
    for team in all_teams:
        if team.lower() in text_lower:
            teams.append(team)
    
    print(f"🏆 Extracted teams: {teams}")
    return teams

def extract_player_from_text(text):
    """Extract player name from text"""
    with closing(get_conn()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM players")
        all_players = [row[0] for row in cursor.fetchall()]
    
    text_lower = text.lower()
    for player in all_players:
        if player.lower() in text_lower:
            print(f"👤 Extracted player: {player}")
            return player
    return None

# --- ENHANCED INTENT HANDLERS ---

def handle_score_intent(teams):
    """Handle score queries"""
    if len(teams) < 2:
        return "Please specify two teams to get the match score."
    
    team1, team2 = teams[0], teams[1]
    
    with closing(get_conn()) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t1.name as home_team, t2.name as away_team, 
                   m.home_score, m.away_score, m.match_date, tourn.name as tournament
            FROM matches m
            JOIN teams t1 ON m.home_team_id = t1.id
            JOIN teams t2 ON m.away_team_id = t2.id  
            JOIN tournaments tourn ON m.tournament_id = tourn.id
            WHERE (t1.name = ? AND t2.name = ?) OR (t1.name = ? AND t2.name = ?)
            ORDER BY m.match_date DESC LIMIT 1
        """, (team1, team2, team2, team1))
        
        match = cursor.fetchone()
        if match:
            return f"{match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']} ({match['tournament']})"
        else:
            return f"No recent match found between {team1} and {team2}."

def handle_stadium_intent(teams):
    """Handle stadium queries"""
    if len(teams) < 2:
        return "Please specify two teams to get the stadium information."
    
    team1, team2 = teams[0], teams[1]
    
    with closing(get_conn()) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.stadium, t1.name as home_team, t2.name as away_team
            FROM matches m
            JOIN teams t1 ON m.home_team_id = t1.id
            JOIN teams t2 ON m.away_team_id = t2.id
            WHERE (t1.name = ? AND t2.name = ?) OR (t1.name = ? AND t2.name = ?)
            ORDER BY m.match_date DESC LIMIT 1
        """, (team1, team2, team2, team1))
        
        match = cursor.fetchone()
        if match:
            return f"The match was played at {match['stadium']}"
        else:
            return f"No stadium information found for {team1} vs {team2}."

def handle_scorers_intent(teams):
    """Handle scorers queries"""
    if len(teams) < 2:
        return "Please specify two teams to get the scorers information."
    
    team1, team2 = teams[0], teams[1]
    
    with closing(get_conn()) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, s.minute, t.name as team_name
            FROM scorers s
            JOIN players p ON s.player_id = p.id
            JOIN teams t ON p.team_id = t.id
            JOIN matches m ON s.match_id = m.id
            JOIN teams t1 ON m.home_team_id = t1.id
            JOIN teams t2 ON m.away_team_id = t2.id
            WHERE (t1.name = ? AND t2.name = ?) OR (t1.name = ? AND t2.name = ?)
            ORDER BY s.minute
        """, (team1, team2, team2, team1))
        
        scorers = cursor.fetchall()
        if scorers:
            scorer_list = [f"{row['name']} ({row['minute']}')" for row in scorers]
            return f"Scorers: {', '.join(scorer_list)}"
        else:
            return f"No scorer information found for {team1} vs {team2}."

def handle_date_intent(teams):
    """Handle date queries"""
    if len(teams) < 2:
        return "Please specify two teams to get the match date."
    
    team1, team2 = teams[0], teams[1]
    
    with closing(get_conn()) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.match_date, t1.name as home_team, t2.name as away_team
            FROM matches m
            JOIN teams t1 ON m.home_team_id = t1.id
            JOIN teams t2 ON m.away_team_id = t2.id
            WHERE (t1.name = ? AND t2.name = ?) OR (t1.name = ? AND t2.name = ?)
            ORDER BY m.match_date DESC LIMIT 1
        """, (team1, team2, team2, team1))
        
        match = cursor.fetchone()
        if match:
            return f"The match was played on {match['match_date']}"
        else:
            return f"No match date found for {team1} vs {team2}."

def handle_tournament_intent(teams):
    """Handle tournament queries"""
    if len(teams) < 2:
        return "Please specify two teams to get the tournament information."
    
    team1, team2 = teams[0], teams[1]
    
    with closing(get_conn()) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tourn.name as tournament, t1.name as home_team, t2.name as away_team
            FROM matches m
            JOIN teams t1 ON m.home_team_id = t1.id
            JOIN teams t2 ON m.away_team_id = t2.id
            JOIN tournaments tourn ON m.tournament_id = tourn.id
            WHERE (t1.name = ? AND t2.name = ?) OR (t1.name = ? AND t2.name = ?)
            ORDER BY m.match_date DESC LIMIT 1
        """, (team1, team2, team2, team1))
        
        match = cursor.fetchone()
        if match:
            return f"The match was part of the {match['tournament']}"
        else:
            return f"No tournament information found for {team1} vs {team2}."

# --- NEW INTENT HANDLERS ---

def handle_player_stats_intent(text):
    """Handle player statistics queries"""
    player_name = extract_player_from_text(text)
    if not player_name:
        return "Please specify a player name to get their statistics."
    
    with closing(get_conn()) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, p.goals, p.appearances, p.position, t.name as team_name
            FROM players p
            JOIN teams t ON p.team_id = t.id
            WHERE p.name = ?
        """, (player_name,))
        
        player = cursor.fetchone()
        if player:
            return f"{player['name']} ({player['team_name']}) - Position: {player['position']}, Goals: {player['goals']}, Appearances: {player['appearances']}"
        else:
            return f"No statistics found for player {player_name}."

def handle_team_ranking_intent(teams):
    """Handle team ranking queries"""
    if not teams:
        return "Please specify a team to get their ranking."
    
    team_name = teams[0]
    
    with closing(get_conn()) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ts.position, ts.points, ts.matches_played, ts.wins, ts.draws, ts.losses,
                   t.name as team_name, tourn.name as tournament
            FROM team_standings ts
            JOIN teams t ON ts.team_id = t.id
            JOIN tournaments tourn ON ts.tournament_id = tourn.id
            WHERE t.name = ?
            ORDER BY ts.points DESC LIMIT 1
        """, (team_name,))
        
        standing = cursor.fetchone()
        if standing:
            return f"{standing['team_name']} is currently {standing['position']} in the {standing['tournament']} with {standing['points']} points ({standing['wins']}W-{standing['draws']}D-{standing['losses']}L)"
        else:
            return f"No ranking information found for {team_name}."

def handle_head_to_head_intent(teams):
    """Handle head-to-head record queries"""
    if len(teams) < 2:
        return "Please specify two teams to get their head-to-head record."
    
    team1, team2 = teams[0], teams[1]
    
    with closing(get_conn()) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_matches,
                SUM(CASE WHEN (t1.name = ? AND m.home_score > m.away_score) OR 
                              (t2.name = ? AND m.away_score > m.home_score) THEN 1 ELSE 0 END) as team1_wins,
                SUM(CASE WHEN (t2.name = ? AND m.home_score > m.away_score) OR 
                              (t1.name = ? AND m.away_score > m.home_score) THEN 1 ELSE 0 END) as team2_wins,
                SUM(CASE WHEN m.home_score = m.away_score THEN 1 ELSE 0 END) as draws
            FROM matches m
            JOIN teams t1 ON m.home_team_id = t1.id
            JOIN teams t2 ON m.away_team_id = t2.id
            WHERE (t1.name = ? AND t2.name = ?) OR (t1.name = ? AND t2.name = ?)
        """, (team1, team1, team2, team2, team1, team2, team2, team1))
        
        record = cursor.fetchone()
        if record and record['total_matches'] > 0:
            return f"Head-to-head: {team1} and {team2} have met {record['total_matches']} times. {team1}: {record['team1_wins']} wins, {team2}: {record['team2_wins']} wins, Draws: {record['draws']}"
        else:
            return f"No head-to-head record found between {team1} and {team2}."

def handle_next_match_intent(teams):
    """Handle next match queries"""
    if not teams:
        return "Please specify a team to get their next match."
    
    team_name = teams[0]
    
    # For now, return a placeholder since we don't have future matches
    return f"Next match information for {team_name} is not available in the current database. This feature will show upcoming fixtures."

def handle_league_top_scorer_intent():
    """Handle top scorer queries"""
    with closing(get_conn()) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, p.goals, t.name as team_name, p.position
            FROM players p
            JOIN teams t ON p.team_id = t.id
            WHERE p.goals > 0
            ORDER BY p.goals DESC
            LIMIT 1
        """, )
        
        top_scorer = cursor.fetchone()
        if top_scorer:
            return f"{top_scorer['name']} ({top_scorer['team_name']}) is the current top scorer with {top_scorer['goals']} goals"
        else:
            return "No top scorer information available."

@lru_cache(maxsize=32)
def llm_reply(user_text):
    """Enhanced LLM fallback with caching"""
    if not OPENROUTER_API_KEY:
        return "I understand your question, but I'm not sure how to respond right now. Try asking about specific match details!"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful sports chatbot. Provide brief, accurate responses about sports. If you don't know something, say so briefly."},
            {"role": "user", "content": user_text}
        ],
        "max_tokens": 150,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                reply = result['choices'][0]['message']['content'].strip()
                return reply if reply else "I understand your question, but I'm not sure how to respond right now. Try asking about specific match details!"
            return "I understand your question, but I'm not sure how to respond right now. Try asking about specific match details!"
        else:
            print(f"LLM API error: {response.status_code}")
            return "I understand your question, but I'm not sure how to respond right now. Try asking about specific match details!"
    except Exception as e:
        print(f"LLM error: {e}")
        return "I understand your question, but I'm not sure how to respond right now. Try asking about specific match details!"

# --- ROUTES ---

@app.route('/health')
def health():
    model_status = "✅ Enhanced model loaded" if intent_model else "⚠️ No model"
    db_status = "✅ Connected"
    
    try:
        with closing(get_conn()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM matches")
            match_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM players") 
            player_count = cursor.fetchone()[0]
        db_status = f"✅ Connected ({match_count} matches, {player_count} players)"
    except Exception as e:
        db_status = f"❌ Database error: {e}"
    
    return jsonify({
        "status": "healthy",
        "model": model_status,
        "database": db_status,
        "llm_configured": bool(OPENROUTER_API_KEY),
        "version": "enhanced_v2.0"
    })

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    # Get intent prediction
    intent, confidence = intent_with_conf(message)
    print(f"📝 Question: {message}")
    
    if intent and confidence >= CONF_THRESHOLD:
        print(f"🎯 Using structured response for intent: {intent}")
        
        # Handle different intents
        if intent in ['score', 'stadium', 'scorers', 'date', 'tournament']:
            teams = extract_teams_from_text(message)
            
            if intent == 'score':
                response = handle_score_intent(teams)
            elif intent == 'stadium':
                response = handle_stadium_intent(teams)
            elif intent == 'scorers':
                response = handle_scorers_intent(teams)
            elif intent == 'date':
                response = handle_date_intent(teams)
            elif intent == 'tournament':
                response = handle_tournament_intent(teams)
        
        elif intent == 'player_stats':
            response = handle_player_stats_intent(message)
        
        elif intent == 'team_ranking':
            teams = extract_teams_from_text(message)
            response = handle_team_ranking_intent(teams)
        
        elif intent == 'head_to_head':
            teams = extract_teams_from_text(message)
            response = handle_head_to_head_intent(teams)
        
        elif intent == 'next_match':
            teams = extract_teams_from_text(message)
            response = handle_next_match_intent(teams)
        
        elif intent == 'league_top_scorer':
            response = handle_league_top_scorer_intent()
        
        else:
            response = f"I recognize this as a {intent} question, but I need more specific information to help you."
        
        return jsonify({
            "response": response,
            "intent": intent,
            "confidence": round(confidence, 3),
            "method": "structured"
        })
    else:
        print(f"🤖 Using LLM fallback (confidence: {confidence:.3f})")
        response = llm_reply(message)
        return jsonify({
            "response": response,
            "intent": intent,
            "confidence": round(confidence, 3) if confidence else 0,
            "method": "llm"
        })

@app.route('/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint with better response formatting"""
    return ask()  # Use the same logic as ask endpoint

@app.route('/llm_test', methods=['GET'])
def llm_test():
    test_response = llm_reply("Hello, can you tell me about football?")
    return jsonify({"test_response": test_response, "configured": bool(OPENROUTER_API_KEY)})

if __name__ == '__main__':
    print("🚀 Starting Enhanced Sports Chatbot Backend...")
    print(f"📊 Model: {'Enhanced' if 'enhanced' in MODEL_PATH else 'Standard'}")
    print(f"🎯 Confidence Threshold: {CONF_THRESHOLD}")
    print(f"🔑 LLM Configured: {bool(OPENROUTER_API_KEY)}")
    app.run(debug=True, host='0.0.0.0', port=5000)