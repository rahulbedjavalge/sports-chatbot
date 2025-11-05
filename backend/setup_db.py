import json, sqlite3, os

DB_PATH = os.path.join("backend", "db.sqlite3")
SEED_PATH = os.path.join("backend", "data", "seed_matches.json")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.executescript("""
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS scorers;
DROP TABLE IF EXISTS matches;

CREATE TABLE matches(
  match_id INTEGER PRIMARY KEY,
  sport TEXT NOT NULL,
  tournament TEXT,
  home_team TEXT NOT NULL,
  away_team TEXT NOT NULL,
  home_score INTEGER NOT NULL,
  away_score INTEGER NOT NULL,
  stadium TEXT,
  date TEXT,
  player_of_match TEXT
);

CREATE TABLE scorers(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  match_id INTEGER NOT NULL,
  player_name TEXT NOT NULL,
  team TEXT,
  FOREIGN KEY(match_id) REFERENCES matches(match_id) ON DELETE CASCADE
);
""")

# NOTE: read JSON with utf-8-sig to ignore BOM
with open(SEED_PATH, "r", encoding="utf-8-sig") as f:
    data = json.load(f)

for m in data:
    cur.execute(
        """INSERT INTO matches(match_id, sport, tournament, home_team, away_team,
           home_score, away_score, stadium, date, player_of_match)
           VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (
            m["match_id"], m["sport"], m.get("tournament"),
            m["home_team"], m["away_team"],
            m["home_score"], m["away_score"],
            m.get("stadium"), m.get("date"), m.get("player_of_match")
        )
    )
    for s in m.get("scorers", []):
        cur.execute(
            "INSERT INTO scorers(match_id, player_name, team) VALUES(?,?,?)",
            (m["match_id"], s["name"], s.get("team"))
        )

conn.commit()

c1 = cur.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
c2 = cur.execute("SELECT COUNT(*) FROM scorers").fetchone()[0]
print(f"Loaded {c1} matches and {c2} scorer rows into {DB_PATH}")
conn.close()
