# Enhanced Training Data Generator for Sports Chatbot
import csv
import random
from pathlib import Path

# Extended teams list with more variety
TEAMS = [
    "Alpha FC", "Beta United", "Gamma Town", "Delta Rovers", "Epsilon City",
    "Zeta FC", "Eta Sports", "Theta United", "Iota Rangers", "Kappa Athletic",
    "Lambda FC", "Mu United", "Nu City", "Xi Rangers", "Omicron FC",
    "Pi United", "Rho Athletic", "Sigma FC", "Tau City", "Upsilon United",
    "Phi Rangers", "Chi Athletic", "Psi FC", "Omega SC", "Berlin Bears",
    "Hamburg Hawks", "Munich Lions", "Dresden Eagles", "Cologne Wolves",
    "Frankfurt Tigers", "Stuttgart Bulls", "Dortmund Warriors", "Leipzig Knights",
    "Hannover Giants", "Bremen Pirates", "Nuremberg Sharks", "Freiburg Panthers",
    "Mainz Falcons", "Hoffenheim Thunder", "Augsburg Lightning"
]

STADIUMS = [
    "National Stadium", "City Arena", "Metropolitan Ground", "Olympic Stadium",
    "Central Park Stadium", "Riverside Arena", "Victory Ground", "Unity Stadium",
    "Champions Arena", "Freedom Stadium", "Liberty Ground", "Excellence Arena",
    "Premier Stadium", "Elite Ground", "Supreme Arena", "Royal Stadium",
    "Empire Ground", "Legacy Arena", "Heritage Stadium", "Future Ground"
]

TOURNAMENTS = [
    "Premier League", "Champions Cup", "Europa League", "City Cup",
    "National Championship", "Regional Trophy", "Super Cup", "Elite Cup",
    "Victory Tournament", "Unity League", "Freedom Cup", "Excellence Trophy",
    "Premier Tournament", "Elite Championship", "Supreme League", "Royal Cup"
]

PLAYERS = [
    "Rodriguez", "Smith", "Johnson", "Williams", "Brown", "Davis", "Miller",
    "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White",
    "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
    "Clark", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "King",
    "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Nelson",
    "Carter", "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell",
    "Parker", "Evans", "Edwards", "Collins", "Stewart", "Sanchez", "Morris"
]

# New intent templates
INTENT_TEMPLATES = {
    'score': [
        "What was the final score of {team1} vs {team2}?",
        "Final result {team1} against {team2}?", 
        "Score of the {team1} {team2} match?",
        "Tell me the scoreline for {team1} vs {team2}",
        "Result between {team1} and {team2}?",
        "What was the score in {team1} vs {team2}?",
        "Final score {team1} against {team2} please",
        "Give me the result of {team1} vs {team2}",
        "Score for {team1} vs {team2} match?",
        "What was the final result {team1} vs {team2}?"
    ],
    
    'stadium': [
        "Where was {team1} vs {team2} played?",
        "Which stadium hosted {team1} against {team2}?",
        "What venue was used for {team1} vs {team2}?",
        "Tell me the ground for {team1} vs {team2}",
        "Stadium for {team1} against {team2}?",
        "Where did {team1} play {team2}?",
        "Which ground hosted {team1} vs {team2}?",
        "Venue for the {team1} {team2} match?",
        "What stadium was {team1} vs {team2} at?",
        "Ground for {team1} against {team2}?"
    ],
    
    'scorers': [
        "Who scored in {team1} vs {team2}?",
        "Scorers for {team1} against {team2}?",
        "Who were the goal scorers in {team1} vs {team2}?",
        "Tell me the scorers for {team1} vs {team2}",
        "Who scored goals in {team1} against {team2}?",
        "Goal scorers {team1} vs {team2}?",
        "Who found the net in {team1} vs {team2}?",
        "Goalscorers for {team1} against {team2}?",
        "Who scored in the {team1} {team2} match?",
        "Tell me who scored for {team1} vs {team2}"
    ],
    
    'date': [
        "When was {team1} vs {team2} played?",
        "Date of {team1} against {team2}?",
        "When did {team1} play {team2}?",
        "What was the match date for {team1} vs {team2}?",
        "Date for {team1} vs {team2}?",
        "When was the {team1} {team2} match?",
        "Match date {team1} against {team2}?",
        "What date was {team1} vs {team2}?",
        "When did the {team1} vs {team2} game happen?",
        "Date of the {team1} against {team2} match?"
    ],
    
    'tournament': [
        "What tournament was {team1} vs {team2}?",
        "Which competition was {team1} against {team2}?",
        "Tournament for {team1} vs {team2}?",
        "What competition was the {team1} {team2} match?",
        "Which tournament hosted {team1} vs {team2}?",
        "Competition for {team1} against {team2}?",
        "What league was {team1} vs {team2} in?",
        "Which tournament was the {team1} vs {team2} match part of?",
        "Competition name for {team1} against {team2}?",
        "Tournament of {team1} vs {team2}?"
    ],
    
    # NEW INTENTS
    'player_stats': [
        "How many goals has {player} scored?",
        "What are {player}'s stats?",
        "Tell me about {player}'s performance",
        "Goals scored by {player}?",
        "{player} statistics please",
        "How is {player} performing this season?",
        "Show me {player}'s goal record",
        "What are {player}'s career stats?",
        "{player} goal count?",
        "Performance stats for {player}?"
    ],
    
    'team_ranking': [
        "What is {team1}'s position in the league?",
        "Where does {team1} rank?", 
        "League position of {team1}?",
        "Tell me {team1}'s ranking",
        "What place is {team1} in?",
        "Current position of {team1}?",
        "League table position for {team1}?",
        "Where is {team1} in the standings?",
        "Ranking of {team1} in the league?",
        "What's {team1}'s league position?"
    ],
    
    'head_to_head': [
        "Head to head record {team1} vs {team2}?",
        "Historical record between {team1} and {team2}?",
        "Past matches {team1} vs {team2}?",
        "All time record {team1} against {team2}?",
        "History between {team1} and {team2}?",
        "Previous meetings {team1} vs {team2}?",
        "Overall record {team1} vs {team2}?",
        "Historical results {team1} against {team2}?",
        "Past results between {team1} and {team2}?",
        "All matches {team1} vs {team2}?"
    ],
    
    'next_match': [
        "When is {team1}'s next match?",
        "Next game for {team1}?",
        "Upcoming fixture for {team1}?",
        "When does {team1} play next?",
        "Next match {team1}?",
        "Upcoming game {team1}?",
        "When is {team1} playing next?",
        "Next fixture for {team1}?",
        "Upcoming match for {team1}?",
        "When does {team1} play again?"
    ],
    
    'league_top_scorer': [
        "Who is the top scorer in the league?",
        "League's leading goalscorer?",
        "Top goal scorer this season?",
        "Who has scored the most goals?",
        "Leading scorer in the tournament?",
        "Highest goalscorer?",
        "Top scorer standings?",
        "Who leads the scoring charts?",
        "Most goals scored by whom?",
        "Golden boot leader?"
    ]
}

ANSWER_TEMPLATES = {
    'score': "{home_team} {home_score}-{away_score} {away_team}",
    'stadium': "{stadium}",
    'scorers': "{scorers}",
    'date': "{date}",
    'tournament': "{tournament}",
    'player_stats': "{player} has scored {goals} goals in {appearances} appearances this season",
    'team_ranking': "{team} is currently {position} in the {tournament} standings",
    'head_to_head': "{team1} and {team2} have met {meetings} times. {team1} has won {wins1}, {team2} has won {wins2}, with {draws} draws",
    'next_match': "{team}'s next match is against {opponent} on {date} at {stadium}",
    'league_top_scorer': "{player} is the current top scorer with {goals} goals"
}

def generate_enhanced_dataset():
    """Generate enhanced training dataset with more variety and new intents"""
    
    data = []
    
    # Generate more examples for existing intents
    for intent, templates in INTENT_TEMPLATES.items():
        if intent in ['score', 'stadium', 'scorers', 'date', 'tournament']:
            # Generate 100 examples per existing intent
            for _ in range(100):
                template = random.choice(templates)
                team1 = random.choice(TEAMS)
                team2 = random.choice([t for t in TEAMS if t != team1])
                
                question = template.format(team1=team1, team2=team2)
                answer_template = ANSWER_TEMPLATES[intent]
                
                data.append({
                    'text': question,
                    'intent': intent,
                    'answer_template': answer_template
                })
        
        elif intent in ['player_stats', 'league_top_scorer']:
            # Generate 50 examples for player-related intents
            for _ in range(50):
                template = random.choice(templates)
                player = random.choice(PLAYERS)
                
                question = template.format(player=player)
                answer_template = ANSWER_TEMPLATES[intent]
                
                data.append({
                    'text': question,
                    'intent': intent,
                    'answer_template': answer_template
                })
                
        elif intent in ['team_ranking', 'next_match']:
            # Generate 50 examples for team-related intents
            for _ in range(50):
                template = random.choice(templates)
                team1 = random.choice(TEAMS)
                
                question = template.format(team1=team1, team=team1)
                answer_template = ANSWER_TEMPLATES[intent]
                
                data.append({
                    'text': question,
                    'intent': intent,
                    'answer_template': answer_template
                })
                
        elif intent == 'head_to_head':
            # Generate 50 examples for head-to-head
            for _ in range(50):
                template = random.choice(templates)
                team1 = random.choice(TEAMS)
                team2 = random.choice([t for t in TEAMS if t != team1])
                
                question = template.format(team1=team1, team2=team2)
                answer_template = ANSWER_TEMPLATES[intent]
                
                data.append({
                    'text': question,
                    'intent': intent,
                    'answer_template': answer_template
                })
    
    return data

if __name__ == "__main__":
    print("Generating enhanced training dataset...")
    
    # Generate new enhanced dataset
    enhanced_data = generate_enhanced_dataset()
    
    # Read existing data
    existing_data = []
    csv_path = Path("data/questions.csv")
    
    if csv_path.exists():
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_data.append(row)
    
    # Combine and shuffle
    all_data = existing_data + enhanced_data
    random.shuffle(all_data)
    
    # Write to new enhanced file
    enhanced_csv_path = Path("data/questions_enhanced.csv")
    
    with open(enhanced_csv_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['text', 'intent', 'answer_template']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)
    
    print(f"Enhanced dataset saved to {enhanced_csv_path}")
    print(f"Total samples: {len(all_data)}")
    print(f"Original samples: {len(existing_data)}")
    print(f"New samples: {len(enhanced_data)}")
    
    # Print intent distribution
    intent_counts = {}
    for item in all_data:
        intent = item['intent']
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
    
    print("\nIntent distribution:")
    for intent, count in sorted(intent_counts.items()):
        print(f"  {intent}: {count}")