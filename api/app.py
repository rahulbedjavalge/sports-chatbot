# Vercel-optimized Flask app
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv

# --- CONFIG ---
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)
CORS(app, origins=["*"])

# Simplified mock data for Vercel deployment
MOCK_DATA = {
    "matches": [
        {
            "id": 1,
            "home_team": "Alpha FC",
            "away_team": "Beta United", 
            "home_score": 2,
            "away_score": 1,
            "date": "2024-11-01",
            "stadium": "Alpha Stadium",
            "tournament": "City Cup"
        },
        {
            "id": 2,
            "home_team": "Gamma Town",
            "away_team": "Delta Rovers",
            "home_score": 1,
            "away_score": 3,
            "date": "2024-11-02", 
            "stadium": "Gamma Arena",
            "tournament": "Premier League"
        }
    ],
    "players": {
        "Alpha FC": ["Rodriguez", "Smith", "Johnson"],
        "Beta United": ["Williams", "Brown", "Davis"],
        "Gamma Town": ["Miller", "Wilson", "Moore"],
        "Delta Rovers": ["Taylor", "Anderson", "Thomas"]
    },
    "standings": {
        "Premier League": [
            {"team": "Alpha FC", "position": 1, "points": 45},
            {"team": "Beta United", "position": 2, "points": 40},
            {"team": "Delta Rovers", "position": 3, "points": 35},
            {"team": "Gamma Town", "position": 4, "points": 30}
        ]
    }
}

def extract_teams_from_text(text):
    """Extract team names from text"""
    teams = []
    text_lower = text.lower()
    
    all_teams = ["Alpha FC", "Beta United", "Gamma Town", "Delta Rovers", 
                "Epsilon City", "Zeta FC", "Berlin Bears", "Hamburg Hawks"]
    
    for team in all_teams:
        if team.lower() in text_lower:
            teams.append(team)
    
    return teams[:2]  # Return max 2 teams

def get_match_info(team1, team2):
    """Get match information between two teams"""
    for match in MOCK_DATA["matches"]:
        if ((match["home_team"] == team1 and match["away_team"] == team2) or 
            (match["home_team"] == team2 and match["away_team"] == team1)):
            return match
    return None

def classify_intent(text):
    """Enhanced intent classification with better patterns"""
    text_lower = text.lower()
    
    # Score-related keywords
    if any(word in text_lower for word in ["score", "result", "final", "scoreline", "won", "beat", "defeat", "win", "lose", "lost"]):
        return "score", 0.95
    elif any(word in text_lower for word in ["stadium", "venue", "ground", "where played", "location", "arena"]):
        return "stadium", 0.95
    elif any(word in text_lower for word in ["scorer", "goal", "who scored", "goalscorer", "scored by"]):
        return "scorers", 0.95
    elif any(word in text_lower for word in ["date", "when", "day", "time", "played on"]):
        return "date", 0.95
    elif any(word in text_lower for word in ["tournament", "competition", "league", "cup", "championship"]):
        return "tournament", 0.95
    elif any(word in text_lower for word in ["ranking", "position", "table", "standing", "rank"]):
        return "team_ranking", 0.95
    elif any(word in text_lower for word in ["top scorer", "leading scorer", "most goals", "highest scorer"]):
        return "league_top_scorer", 0.95
    # Default to score intent for team vs team questions
    elif " vs " in text_lower or " against " in text_lower or " v " in text_lower:
        return "score", 0.8
    else:
        return "general", 0.2

def llm_fallback(text):
    """Fast fallback for general questions"""
    # Quick responses for common questions without API calls
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["hello", "hi", "hey", "greetings"]):
        return "Hello! I'm your sports assistant. Ask me about match scores, stadiums, dates, tournaments, or player stats!"
    
    if any(word in text_lower for word in ["help", "what can you do", "commands"]):
        return "I can help you with: match scores, stadium info, goal scorers, match dates, tournaments, team rankings, and top scorers. Try asking 'What was the score of Alpha FC vs Beta United?'"
    
    if any(word in text_lower for word in ["thanks", "thank you", "appreciate"]):
        return "You're welcome! Feel free to ask about any sports information."
    
    # Only call LLM API for complex questions if configured
    if not OPENROUTER_API_KEY:
        return "I understand your question, but I'm optimized for specific sports queries. Try asking about match details like scores, stadiums, or tournaments!"
    
    # For complex questions, use LLM (but with timeout)
    import requests
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "tngtech/deepseek-r1t2-chimera:free",
        "messages": [
            {"role": "system", "content": "You are a helpful sports chatbot. Provide brief responses in 1-2 sentences. If you don't know something, suggest asking about specific match details."},
            {"role": "user", "content": text}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        print("🤖 Making LLM API call...")
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                               headers=headers, json=data, timeout=5)  # Reduced timeout
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                reply = result['choices'][0]['message']['content'].strip()
                return reply if reply else "I understand your question. Try asking about specific match details!"
    except Exception as e:
        print(f"LLM API timeout/error: {e}")
    
    return "I understand your question. Try asking about specific match details like scores, stadiums, or tournaments!"

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "version": "vercel_v1.0",
        "llm_configured": bool(OPENROUTER_API_KEY),
        "matches_count": len(MOCK_DATA["matches"])
    })

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    import time
    start_time = time.time()
    
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({"answer": "Please provide a message."}), 400
    
    print(f"📝 Question: {message}")
    
    # Classify intent
    intent, confidence = classify_intent(message)
    print(f"🎯 Intent: {intent}, Confidence: {confidence}")
    
    if intent != "general" and confidence >= 0.5:  # Lowered threshold for faster responses
        teams = extract_teams_from_text(message)
        
        if intent in ["score", "stadium", "scorers", "date", "tournament"]:
            if len(teams) < 2:
                answer = "Please mention two teams for match information (e.g., 'Alpha FC vs Beta United')."
            else:
                match = get_match_info(teams[0], teams[1])
                if not match:
                    answer = f"No match found between {teams[0]} and {teams[1]} in our data."
                else:
                    if intent == "score":
                        answer = f"{match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']} ({match['tournament']})"
                    elif intent == "stadium":
                        answer = f"The match was played at {match['stadium']}"
                    elif intent == "scorers":
                        # Mock scorers based on teams
                        home_players = MOCK_DATA["players"].get(match['home_team'], ["Player A"])
                        away_players = MOCK_DATA["players"].get(match['away_team'], ["Player B"])
                        answer = f"Scorers: {home_players[0]} (15'), {away_players[0]} (42'), {home_players[1] if len(home_players) > 1 else home_players[0]} (78')"
                    elif intent == "date":
                        answer = f"The match was played on {match['date']}"
                    elif intent == "tournament":
                        answer = f"The match was part of the {match['tournament']}"
        
        elif intent == "team_ranking":
            if not teams:
                answer = "Please specify a team to get their ranking."
            else:
                team_name = teams[0]
                # Find team in standings
                for league, standings in MOCK_DATA["standings"].items():
                    for team_info in standings:
                        if team_info["team"] == team_name:
                            answer = f"{team_name} is currently {team_info['position']} in the {league} with {team_info['points']} points"
                            break
                    else:
                        continue
                    break
                else:
                    answer = f"No ranking information found for {team_name}"
        
        elif intent == "league_top_scorer":
            answer = "Rodriguez (Alpha FC) is the current top scorer with 12 goals this season"
        
        else:
            answer = "I understand your question, but I need more specific information to help you."
        
        return jsonify({
            "answer": answer,
            "intent": intent,
            "confidence": round(confidence, 3),
            "method": "structured",
            "response_time": round(time.time() - start_time, 3)
        })
    
    else:
        # Use LLM fallback
        print(f"🤖 Using fast fallback")
        answer = llm_fallback(message)
        
        return jsonify({
            "answer": answer,
            "intent": intent,
            "confidence": round(confidence, 3),
            "method": "fallback",
            "response_time": round(time.time() - start_time, 3)
        })

@app.route('/api/ask', methods=['POST'])
def ask():
    """Alias for chat endpoint"""
    return chat()

# For Vercel
def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    print("🚀 Starting Vercel-compatible API server...")
    print("📡 Health endpoint: http://127.0.0.1:5000/api/health")
    print("💬 Chat endpoint: http://127.0.0.1:5000/api/chat")
    app.run(debug=True, host='0.0.0.0', port=5000)