import csv, os, random, sqlite3, itertools, re
from datetime import datetime

DB_PATH = r"backend\db.sqlite3"
OUT_PATH = r"nlp\data\questions.csv"
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
rows = conn.execute("select * from matches").fetchall()
conn.close()

def team_short(name):
    return re.sub(r"\s+(FC|SC|United|Town|Rovers|Bears|Hawks)$", "", name, flags=re.I)

data = []
random.seed(7)

for r in rows:
    home = r["home_team"]; away = r["away_team"]
    home_s = team_short(home); away_s = team_short(away)
    score = f"{r['home_score']}-{r['away_score']}"
    date = r['date'] or "—"
    stadium = r['stadium'] or "—"
    tournament = r['tournament'] or "—"

    # SCORE variants
    score_prompts = [
        "What was the score between {home} and {away}?",
        "Who won {home} vs {away}?",
        "Give me the final result: {home} vs {away}.",
        "Result for {home} against {away}?",
        "Scoreline {home} vs {away} please.",
        "Final score of {home} vs {away}?"
    ]

    # STADIUM variants
    stadium_prompts = [
        "Where was {home} vs {away} played?",
        "Which stadium hosted {home} against {away}?",
        "Stadium for {home} vs {away}?",
        "What venue was used for {home} vs {away}?",
        "Tell me the ground for {home} vs {away}."
    ]

    # SCORERS variants
    scorers_prompts = [
        "Who scored in {home} vs {away}?",
        "List the goal scorers in {home} vs {away}.",
        "Who were the scorers for {home} against {away}?",
        "Scorers for {home} vs {away}?"
    ]

    # DATE variants
    date_prompts = [
        "When did {home} play {away}?",
        "What was the match date for {home} vs {away}?",
        "Date of {home} against {away}?"
    ]

    # TOURNAMENT variants
    tourn_prompts = [
        "Which tournament was {home} vs {away}?",
        "What competition was {home} vs {away}?",
        "Tournament for {home} against {away}?"
    ]

    # Build examples with both full and short team names
    teams = {(home, away), (home_s, away_s), (home, away_s), (home_s, away)}

    for h, a in teams:
        for t in score_prompts:
            data.append( (t.format(home=h, away=a), "score", "{home_team} {home_score}-{away_score} {away_team}") )
        for t in stadium_prompts:
            data.append( (t.format(home=h, away=a), "stadium", "{stadium}") )
        for t in scorers_prompts:
            data.append( (t.format(home=h, away=a), "scorers", "{scorers}") )
        for t in date_prompts:
            data.append( (t.format(home=h, away=a), "date", "{date}") )
        for t in tourn_prompts:
            data.append( (t.format(home=h, away=a), "tournament", "{tournament}") )

# Light shuffling and trimming to ~150–250 examples
random.shuffle(data)
data = data[:250]

with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["text","intent","answer_template"])
    w.writerows(data)

print(f" Wrote {len(data)} examples to {OUT_PATH}")
