# Enhanced Database Setup with More Sports Data
import sqlite3
import json
import random
from datetime import datetime, timedelta

def create_enhanced_database():
    """Create enhanced database with more comprehensive sports data"""
    
    # Connect to database
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    # Drop existing tables to recreate with new schema
    cursor.execute('DROP TABLE IF EXISTS scorers')
    cursor.execute('DROP TABLE IF EXISTS matches')
    cursor.execute('DROP TABLE IF EXISTS players')
    cursor.execute('DROP TABLE IF EXISTS teams')
    cursor.execute('DROP TABLE IF EXISTS tournaments')
    cursor.execute('DROP TABLE IF EXISTS team_standings')

    # Create enhanced tables
    cursor.execute('''
        CREATE TABLE tournaments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            season TEXT NOT NULL,
            start_date DATE,
            end_date DATE
        )
    ''')

    cursor.execute('''
        CREATE TABLE teams (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT,
            founded_year INTEGER,
            stadium TEXT,
            capacity INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE players (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            team_id INTEGER,
            position TEXT,
            goals INTEGER DEFAULT 0,
            appearances INTEGER DEFAULT 0,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE matches (
            id INTEGER PRIMARY KEY,
            home_team_id INTEGER,
            away_team_id INTEGER,
            home_score INTEGER,
            away_score INTEGER,
            match_date DATE,
            stadium TEXT,
            tournament_id INTEGER,
            FOREIGN KEY (home_team_id) REFERENCES teams(id),
            FOREIGN KEY (away_team_id) REFERENCES teams(id),
            FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE scorers (
            id INTEGER PRIMARY KEY,
            match_id INTEGER,
            player_id INTEGER,
            minute INTEGER,
            FOREIGN KEY (match_id) REFERENCES matches(id),
            FOREIGN KEY (player_id) REFERENCES players(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE team_standings (
            id INTEGER PRIMARY KEY,
            team_id INTEGER,
            tournament TEXT,
            position INTEGER,
            points INTEGER,
            wins INTEGER,
            draws INTEGER,
            losses INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams(id)
        )
    ''')

    # --- Deterministic test data for unit tests ---
    # Insert tournament
    cursor.execute("INSERT INTO tournaments (name, season, start_date, end_date) VALUES (?, ?, ?, ?)",
                   ("City Cup", "2024/2025", "2024-08-01", "2025-05-31"))
    tournament_id = cursor.lastrowid

    # Insert teams
    cursor.execute("INSERT INTO teams (name, city, founded_year, stadium, capacity) VALUES (?, ?, ?, ?, ?)",
                   ("Alpha FC", "Alpha City", 1901, "Alpha Stadium", 40000))
    alpha_id = cursor.lastrowid
    cursor.execute("INSERT INTO teams (name, city, founded_year, stadium, capacity) VALUES (?, ?, ?, ?, ?)",
                   ("Beta United", "Beta Town", 1920, "Beta Arena", 35000))
    beta_id = cursor.lastrowid

    # Insert player
    cursor.execute("INSERT INTO players (name, team_id, position, goals, appearances) VALUES (?, ?, ?, ?, ?)",
                   ("Rodriguez", alpha_id, "Forward", 27, 30))
    rodriguez_id = cursor.lastrowid

    # Insert match between Alpha FC and Beta United on 2024-11-01 at Alpha Stadium in City Cup
    cursor.execute("INSERT INTO matches (home_team_id, away_team_id, home_score, away_score, match_date, stadium, tournament_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (alpha_id, beta_id, 2, 1, "2024-11-01", "Alpha Stadium", tournament_id))
    match_id = cursor.lastrowid

    # Insert scorers for the match
    cursor.execute("INSERT INTO scorers (match_id, player_id, minute) VALUES (?, ?, ?)",
                   (match_id, rodriguez_id, 34))
    # Add another scorer for Beta United
    cursor.execute("INSERT INTO players (name, team_id, position, goals, appearances) VALUES (?, ?, ?, ?, ?)",
                   ("Smith", beta_id, "Midfielder", 10, 28))
    smith_id = cursor.lastrowid
    cursor.execute("INSERT INTO scorers (match_id, player_id, minute) VALUES (?, ?, ?)",
                   (match_id, smith_id, 67))

    # Insert team standings for Premier League and City Cup
    cursor.execute("INSERT INTO team_standings (team_id, tournament, position, points, wins, draws, losses) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (alpha_id, "Premier League", 1, 80, 25, 5, 2))
    cursor.execute("INSERT INTO team_standings (team_id, tournament, position, points, wins, draws, losses) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (alpha_id, "City Cup", 4, 73, 24, 1, 7))

    # Commit changes
    conn.commit()
    conn.close()
    
    cursor.execute('''
        CREATE TABLE team_standings (
            id INTEGER PRIMARY KEY,
            team_id INTEGER,
            tournament_id INTEGER,
            position INTEGER,
            points INTEGER,
            matches_played INTEGER,
            wins INTEGER,
            draws INTEGER,
            losses INTEGER,
            goals_for INTEGER,
            goals_against INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
        )
    ''')
    
    # Insert tournaments
    tournaments = [
        (1, 'Premier League', '2024-25', '2024-08-15', '2025-05-25'),
        (2, 'Champions Cup', '2024-25', '2024-09-01', '2025-06-10'),
        (3, 'Europa League', '2024-25', '2024-09-15', '2025-05-20'),
        (4, 'City Cup', '2024-25', '2024-10-01', '2024-12-20'),
        (5, 'National Championship', '2024-25', '2024-08-20', '2025-05-30')
    ]
    
    cursor.executemany('''
        INSERT INTO tournaments (id, name, season, start_date, end_date) 
        VALUES (?, ?, ?, ?, ?)
    ''', tournaments)
    
    # Insert teams
    teams_data = [
        (1, 'Alpha FC', 'Alpha City', 1920, 'Alpha Stadium', 45000),
        (2, 'Beta United', 'Beta Town', 1925, 'Unity Ground', 42000),
        (3, 'Gamma Town', 'Gamma', 1930, 'Gamma Arena', 38000),
        (4, 'Delta Rovers', 'Delta City', 1915, 'Delta Park', 40000),
        (5, 'Epsilon City', 'Epsilon', 1928, 'Epsilon Stadium', 35000),
        (6, 'Zeta FC', 'Zeta Town', 1922, 'Zeta Ground', 41000),
        (7, 'Eta Sports', 'Eta City', 1935, 'Eta Arena', 33000),
        (8, 'Theta United', 'Theta', 1940, 'Theta Stadium', 36000),
        (9, 'Iota Rangers', 'Iota City', 1918, 'Iota Park', 39000),
        (10, 'Kappa Athletic', 'Kappa Town', 1932, 'Kappa Ground', 37000),
        (11, 'Lambda FC', 'Lambda City', 1927, 'Lambda Stadium', 44000),
        (12, 'Mu United', 'Mu Town', 1924, 'Mu Arena', 34000),
        (13, 'Berlin Bears', 'Berlin', 1905, 'Bear Stadium', 75000),
        (14, 'Hamburg Hawks', 'Hamburg', 1910, 'Hawk Arena', 55000),
        (15, 'Munich Lions', 'Munich', 1900, 'Lion Ground', 70000),
        (16, 'Dresden Eagles', 'Dresden', 1912, 'Eagle Park', 45000),
        (17, 'Cologne Wolves', 'Cologne', 1948, 'Wolf Stadium', 50000),
        (18, 'Frankfurt Tigers', 'Frankfurt', 1899, 'Tiger Ground', 52000),
        (19, 'Stuttgart Bulls', 'Stuttgart', 1893, 'Bull Arena', 60000),
        (20, 'Omega SC', 'Omega City', 1933, 'Omega Stadium', 43000)
    ]
    
    cursor.executemany('''
        INSERT INTO teams (id, name, city, founded_year, stadium, capacity) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', teams_data)
    
    # Insert players
    player_names = [
        'Rodriguez', 'Smith', 'Johnson', 'Williams', 'Brown', 'Davis', 'Miller',
        'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White',
        'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson',
        'Clark', 'Lewis', 'Lee', 'Walker', 'Hall', 'Allen', 'Young', 'King',
        'Wright', 'Lopez', 'Hill', 'Scott', 'Green', 'Adams', 'Baker', 'Nelson'
    ]
    
    positions = ['Forward', 'Midfielder', 'Defender', 'Goalkeeper']
    players_data = []
    player_id = 1
    
    for team_id in range(1, 21):  # 20 teams
        for i in range(25):  # 25 players per team
            name = f"{random.choice(player_names)} {chr(65 + random.randint(0, 25))}"
            position = random.choice(positions)
            goals = random.randint(0, 25) if position == 'Forward' else random.randint(0, 10)
            appearances = random.randint(15, 35)
            
            players_data.append((player_id, name, team_id, position, goals, appearances))
            player_id += 1
    
    cursor.executemany('''
        INSERT INTO players (id, name, team_id, position, goals, appearances) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', players_data)
    
    # Generate match data
    matches_data = []
    match_id = 1
    
    # Generate matches for each tournament
    for tournament_id in range(1, 6):
        for round_num in range(10):  # 10 rounds per tournament
            home_team = random.randint(1, 20)
            away_team = random.randint(1, 20)
            while away_team == home_team:
                away_team = random.randint(1, 20)
            
            home_score = random.randint(0, 5)
            away_score = random.randint(0, 4)
            
            # Generate date within tournament period
            base_date = datetime(2024, 9, 1) + timedelta(days=random.randint(0, 200))
            match_date = base_date.strftime('%Y-%m-%d')
            
            # Get stadium from home team
            cursor.execute('SELECT stadium FROM teams WHERE id = ?', (home_team,))
            stadium = cursor.fetchone()[0]
            
            matches_data.append((match_id, home_team, away_team, home_score, away_score, 
                              match_date, stadium, tournament_id))
            match_id += 1
    
    cursor.executemany('''
        INSERT INTO matches (id, home_team_id, away_team_id, home_score, away_score, 
                           match_date, stadium, tournament_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', matches_data)
    
    # Generate scorer data
    scorers_data = []
    scorer_id = 1
    
    for match in matches_data:
        match_id = match[0]
        home_team_id = match[1]
        away_team_id = match[2]
        home_score = match[3]
        away_score = match[4]
        
        # Add scorers for home team
        for _ in range(home_score):
            cursor.execute('SELECT id FROM players WHERE team_id = ? AND position = "Forward" ORDER BY RANDOM() LIMIT 1', 
                          (home_team_id,))
            player_result = cursor.fetchone()
            if player_result:
                player_id = player_result[0]
                minute = random.randint(1, 90)
                scorers_data.append((scorer_id, match_id, player_id, minute))
                scorer_id += 1
        
        # Add scorers for away team
        for _ in range(away_score):
            cursor.execute('SELECT id FROM players WHERE team_id = ? AND position = "Forward" ORDER BY RANDOM() LIMIT 1', 
                          (away_team_id,))
            player_result = cursor.fetchone()
            if player_result:
                player_id = player_result[0]
                minute = random.randint(1, 90)
                scorers_data.append((scorer_id, match_id, player_id, minute))
                scorer_id += 1
    
    cursor.executemany('''
        INSERT INTO scorers (id, match_id, player_id, minute) 
        VALUES (?, ?, ?, ?)
    ''', scorers_data)
    
    # Generate team standings
    standings_data = []
    standing_id = 1
    for tournament_id in range(1, 6):
        teams_in_tournament = list(range(1, 21))  # All teams participate
        random.shuffle(teams_in_tournament)
        
        for position, team_id in enumerate(teams_in_tournament, 1):
            # Calculate realistic stats based on position
            matches_played = random.randint(25, 35)
            
            if position <= 5:  # Top teams
                win_rate = random.uniform(0.6, 0.8)
            elif position <= 10:  # Mid-table
                win_rate = random.uniform(0.4, 0.6)
            else:  # Bottom teams
                win_rate = random.uniform(0.2, 0.4)
            
            wins = int(matches_played * win_rate)
            losses = random.randint(0, matches_played - wins)
            draws = matches_played - wins - losses
            
            goals_for = random.randint(wins * 1, wins * 3 + draws * 1)
            goals_against = random.randint(losses * 0, losses * 2 + draws * 1)
            
            points = wins * 3 + draws * 1
            
            standings_data.append((standing_id, team_id, tournament_id, position, 
                                points, matches_played, wins, draws, losses, 
                                goals_for, goals_against))
            standing_id += 1
    
    cursor.executemany('''
        INSERT INTO team_standings (id, team_id, tournament_id, position, points, 
                                  matches_played, wins, draws, losses, goals_for, goals_against) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', standings_data)
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("Enhanced database created successfully!")
    print(f"- {len(tournaments)} tournaments")
    print(f"- {len(teams_data)} teams")
    print(f"- {len(players_data)} players")
    print(f"- {len(matches_data)} matches")
    print(f"- {len(scorers_data)} scorer records")
    print(f"- {len(standings_data)} standings records")

if __name__ == "__main__":
    create_enhanced_database()