# url.py
# Mapping of local league and club names to The Odds API and historical data URLs

# List of available leagues
available_leagues = ["Premier League", "Bundesliga", "La Liga", "Serie A", "Primeira Liga", "Ligue 1"]

# Mapping of local league names to The Odds API sport_key
league_to_odds_api = {
    "Premier League": "soccer_epl",
    "Bundesliga": "soccer_germany_bundesliga",
    "La Liga": "soccer_spain_la_liga",
    "Serie A": "soccer_italy_serie_a",
    "Primeira Liga": "soccer_portugal_primeira_liga",
    "Ligue 1": "soccer_france_ligue_one"
}

# Clubs by league (local names used for historical data)
clubs_by_league = {
    "Premier League": [
        "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
        "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich",
        "Leicester", "Liverpool", "Man City", "Man United", "Newcastle",
        "Nott'm Forest", "Southampton", "Tottenham", "West Ham", "Wolves"
    ],
    "Bundesliga": [
        "Augsburg", "Bayern Munich", "Bochum", "Dortmund", "M'gladbach",
        "Ein Frankfurt", "Freiburg", "Heidenheim", "Hoffenheim", "Holstein Kiel",
        "Mainz", "RB Leipzig", "St Pauli", "Stuttgart", "Union Berlin",
        "Werder Bremen", "Wolfsburg", "Leverkusen"
    ],
    "La Liga": [
        "Alaves", "Almeria", "Ath Bilbao", "Ath Madrid", "Barcelona",
        "Celta", "Espanol", "Getafe", "Girona", "Las Palmas",
        "Leganes", "Mallorca", "Osasuna", "Vallecano", "Betis",
        "Real Madrid", "Sociedad", "Sevilla", "Valencia", "Villarreal"
    ],
    "Serie A": [
        "Atalanta", "Bologna", "Cagliari", "Como", "Empoli",
        "Fiorentina", "Genoa", "Inter", "Juventus", "Lazio",
        "Lecce", "Milan", "Monza", "Napoli", "Parma",
        "Roma", "Torino", "Udinese", "Venezia", "Verona"
    ],
    "Primeira Liga": [
        "Arouca", "AVS", "Benfica", "Boavista", "Sp Braga",
        "Casa Pia", "Estoril", "Estrela", "Famalicao", "Farense",
        "Gil Vicente", "Moreirense", "Nacional", "Porto", "Rio Ave",
        "Santa Clara", "Sp Lisbon", "Guimaraes"
    ],
    "Ligue 1": [
        "Angers", "Auxerre", "Brest", "Le Havre", "Lens",
        "Lille", "Lyon", "Marseille", "Monaco", "Montpellier",
        "Nantes", "Nice", "Paris SG", "Reims", "Rennes",
        "St Etienne", "Strasbourg", "Toulouse"
    ]
}

# Mapping of local club names to The Odds API team names
club_to_odds_api = {
    "Arsenal": "Arsenal",
    "Aston Villa": "Aston Villa",
    "Bournemouth": "Bournemouth",
    "Brentford": "Brentford",
    "Brighton": "Brighton and Hove Albion",
    "Chelsea": "Chelsea",
    "Crystal Palace": "Crystal Palace",
    "Everton": "Everton",
    "Fulham": "Fulham",
    "Ipswich": "Ipswich Town",
    "Leicester": "Leicester City",
    "Liverpool": "Liverpool",
    "Man City": "Manchester City",
    "Man United": "Manchester United",
    "Newcastle": "Newcastle United",
    "Nott'm Forest": "Nottingham Forest",
    "Southampton": "Southampton",
    "Tottenham": "Tottenham Hotspur",
    "West Ham": "West Ham United",
    "Wolves": "Wolverhampton Wanderers",
    "Augsburg": "Augsburg",
    "Bayern Munich": "Bayern Munich",
    "Bochum": "Bochum",
    "Dortmund": "Borussia Dortmund",
    "M'gladbach": "Borussia Monchengladbach",
    "Ein Frankfurt": "Eintracht Frankfurt",
    "Freiburg": "Freiburg",
    "Heidenheim": "Heidenheim",
    "Hoffenheim": "Hoffenheim",
    "Holstein Kiel": "Holstein Kiel",
    "Mainz": "Mainz 05",
    "RB Leipzig": "RB Leipzig",
    "St Pauli": "St Pauli",
    "Stuttgart": "Stuttgart",
    "Union Berlin": "Union Berlin",
    "Werder Bremen": "Werder Bremen",
    "Wolfsburg": "Wolfsburg",
    "Leverkusen": "Bayer Leverkusen",
    "Alaves": "Alaves",
    "Almeria": "Almeria",
    "Ath Bilbao": "Athletic Bilbao",
    "Ath Madrid": "Atletico Madrid",
    "Barcelona": "Barcelona",
    "Celta": "Celta Vigo",
    "Espanol": "Espanyol",
    "Getafe": "Getafe",
    "Girona": "Girona",
    "Las Palmas": "Las Palmas",
    "Leganes": "Leganes",
    "Mallorca": "Mallorca",
    "Osasuna": "Osasuna",
    "Vallecano": "Rayo Vallecano",
    "Betis": "Real Betis",
    "Real Madrid": "Real Madrid",
    "Sociedad": "Real Sociedad",
    "Sevilla": "Sevilla",
    "Valencia": "Valencia",
    "Villarreal": "Villarreal",
    "Atalanta": "Atalanta BC",
    "Bologna": "Bologna",
    "Cagliari": "Cagliari",
    "Como": "Como",
    "Empoli": "Empoli",
    "Fiorentina": "Fiorentina",
    "Genoa": "Genoa",
    "Inter": "Inter Milan",
    "Juventus": "Juventus",
    "Lazio": "Lazio",
    "Lecce": "Lecce",
    "Milan": "AC Milan",
    "Monza": "Monza",
    "Napoli": "Napoli",
    "Parma": "Parma",
    "Roma": "AS Roma",
    "Torino": "Torino",
    "Udinese": "Udinese",
    "Venezia": "Venezia",
    "Verona": "Hellas Verona",
    "Arouca": "Arouca",
    "AVS": "AVS",
    "Benfica": "Benfica",
    "Boavista": "Boavista",
    "Sp Braga": "Sporting Braga",
    "Casa Pia": "Casa Pia",
    "Estoril": "Estoril",
    "Estrela": "Estrela Amadora",
    "Famalicao": "Famalicao",
    "Farense": "Farense",
    "Gil Vicente": "Gil Vicente",
    "Moreirense": "Moreirense",
    "Nacional": "Nacional",
    "Porto": "Porto",
    "Rio Ave": "Rio Ave",
    "Santa Clara": "Santa Clara",
    "Sp Lisbon": "Sporting CP",
    "Guimaraes": "Vitoria Guimaraes",
    "Angers": "Angers",
    "Auxerre": "Auxerre",
    "Brest": "Brest",
    "Le Havre": "Le Havre",
    "Lens": "Lens",
    "Lille": "Lille",
    "Lyon": "Lyon",
    "Marseille": "Marseille",
    "Monaco": "Monaco",
    "Montpellier": "Montpellier",
    "Nantes": "Nantes",
    "Nice": "Nice",
    "Paris SG": "Paris Saint-Germain",
    "Reims": "Reims",
    "Rennes": "Rennes",
    "St Etienne": "Saint Etienne",
    "Strasbourg": "Strasbourg",
    "Toulouse": "Toulouse"
}

# URLs for league pages
file_path_leagues = {
    "Premier League": "https://www.football-data.co.uk/englandm.php",
    "Bundesliga": "https://www.football-data.co.uk/germanym.php",
    "La Liga": "https://www.football-data.co.uk/spainm.php",
    "Serie A": "https://www.football-data.co.uk/italym.php",
    "Primeira Liga": "https://www.football-data.co.uk/portugalm.php",
    "Ligue 1": "https://www.football-data.co.uk/francem.php"
}

# Historical data URLs for each league
file_path_premierleague = {
    "premierleague_1516": "https://www.football-data.co.uk/mmz4281/1516/E0.csv",
    "premierleague_1617": "https://www.football-data.co.uk/mmz4281/1617/E0.csv",
    "premierleague_1718": "https://www.football-data.co.uk/mmz4281/1718/E0.csv",
    "premierleague_1819": "https://www.football-data.co.uk/mmz4281/1819/E0.csv",
    "premierleague_1920": "https://www.football-data.co.uk/mmz4281/1920/E0.csv",
    "premierleague_2021": "https://www.football-data.co.uk/mmz4281/2021/E0.csv",
    "premierleague_2122": "https://www.football-data.co.uk/mmz4281/2122/E0.csv",
    "premierleague_2223": "https://www.football-data.co.uk/mmz4281/2223/E0.csv",
    "premierleague_2324": "https://www.football-data.co.uk/mmz4281/2324/E0.csv",
    "premierleague_2425": "https://www.football-data.co.uk/mmz4281/2425/E0.csv"
}

file_path_bundesliga = {
    "bundesliga_1516": "https://www.football-data.co.uk/mmz4281/1516/D1.csv",
    "bundesliga_1617": "https://www.football-data.co.uk/mmz4281/1617/D1.csv",
    "bundesliga_1718": "https://www.football-data.co.uk/mmz4281/1718/D1.csv",
    "bundesliga_1819": "https://www.football-data.co.uk/mmz4281/1819/D1.csv",
    "bundesliga_1920": "https://www.football-data.co.uk/mmz4281/1920/D1.csv",
    "bundesliga_2021": "https://www.football-data.co.uk/mmz4281/2021/D1.csv",
    "bundesliga_2122": "https://www.football-data.co.uk/mmz4281/2122/D1.csv",
    "bundesliga_2223": "https://www.football-data.co.uk/mmz4281/2223/D1.csv",
    "bundesliga_2324": "https://www.football-data.co.uk/mmz4281/2324/D1.csv",
    "bundesliga_2425": "https://www.football-data.co.uk/mmz4281/2425/D1.csv"
}

file_path_laliga = {
    "laliga_1516": "https://www.football-data.co.uk/mmz4281/1516/SP1.csv",
    "laliga_1617": "https://www.football-data.co.uk/mmz4281/1617/SP1.csv",
    "laliga_1718": "https://www.football-data.co.uk/mmz4281/1718/SP1.csv",
    "laliga_1819": "https://www.football-data.co.uk/mmz4281/1819/SP1.csv",
    "laliga_1920": "https://www.football-data.co.uk/mmz4281/1920/SP1.csv",
    "laliga_2021": "https://www.football-data.co.uk/mmz4281/2021/SP1.csv",
    "laliga_2122": "https://www.football-data.co.uk/mmz4281/2122/SP1.csv",
    "laliga_2223": "https://www.football-data.co.uk/mmz4281/2223/SP1.csv",
    "laliga_2324": "https://www.football-data.co.uk/mmz4281/2324/SP1.csv",
    "laliga_2425": "https://www.football-data.co.uk/mmz4281/2425/SP1.csv"
}

file_path_seriea = {
    "seriea_1516": "https://www.football-data.co.uk/mmz4281/1516/I1.csv",
    "seriea_1617": "https://www.football-data.co.uk/mmz4281/1617/I1.csv",
    "seriea_1718": "https://www.football-data.co.uk/mmz4281/1718/I1.csv",
    "seriea_1819": "https://www.football-data.co.uk/mmz4281/1819/I1.csv",
    "seriea_1920": "https://www.football-data.co.uk/mmz4281/1920/I1.csv",
    "seriea_2021": "https://www.football-data.co.uk/mmz4281/2021/I1.csv",
    "seriea_2122": "https://www.football-data.co.uk/mmz4281/2122/I1.csv",
    "seriea_2223": "https://www.football-data.co.uk/mmz4281/2223/I1.csv",
    "seriea_2324": "https://www.football-data.co.uk/mmz4281/2324/I1.csv",
    "seriea_2425": "https://www.football-data.co.uk/mmz4281/2425/I1.csv"
}

file_path_primeiraliga = {
    "portugueseleague_1516": "https://www.football-data.co.uk/mmz4281/1516/P1.csv",
    "portugueseleague_1617": "https://www.football-data.co.uk/mmz4281/1617/P1.csv",
    "portugueseleague_1718": "https://www.football-data.co.uk/mmz4281/1718/P1.csv",
    "portugueseleague_1819": "https://www.football-data.co.uk/mmz4281/1819/P1.csv",
    "portugueseleague_1920": "https://www.football-data.co.uk/mmz4281/1920/P1.csv",
    "portugueseleague_2021": "https://www.football-data.co.uk/mmz4281/2021/P1.csv",
    "portugueseleague_2122": "https://www.football-data.co.uk/mmz4281/2122/P1.csv",
    "portugueseleague_2223": "https://www.football-data.co.uk/mmz4281/2223/P1.csv",
    "portugueseleague_2324": "https://www.football-data.co.uk/mmz4281/2324/P1.csv",
    "portugueseleague_2425": "https://www.football-data.co.uk/mmz4281/2425/P1.csv"
}

file_path_ligue1 = {
    "ligue1_1516": "https://www.football-data.co.uk/mmz4281/1516/F1.csv",
    "ligue1_1617": "https://www.football-data.co.uk/mmz4281/1617/F1.csv",
    "ligue1_1718": "https://www.football-data.co.uk/mmz4281/1718/F1.csv",
    "ligue1_1819": "https://www.football-data.co.uk/mmz4281/1819/F1.csv",
    "ligue1_1920": "https://www.football-data.co.uk/mmz4281/1920/F1.csv",
    "ligue1_2021": "https://www.football-data.co.uk/mmz4281/2021/F1.csv",
    "ligue1_2122": "https://www.football-data.co.uk/mmz4281/2122/F1.csv",
    "ligue1_2223": "https://www.football-data.co.uk/mmz4281/2223/F1.csv",
    "ligue1_2324": "https://www.football-data.co.uk/mmz4281/2324/F1.csv",
    "ligue1_2425": "https://www.football-data.co.uk/mmz4281/2425/F1.csv"
}

# Combine all league file paths
league_file_paths = {
    "Premier League": file_path_premierleague,
    "Bundesliga": file_path_bundesliga,
    "La Liga": file_path_laliga,
    "Serie A": file_path_seriea,
    "Primeira Liga": file_path_primeiraliga,
    "Ligue 1": file_path_ligue1
}

def file_path_builder(var_league, var_firstseason, var_lastseason):
    """Build a list of CSV file paths for a given league and season range."""
    if var_league in league_file_paths:
        league_paths = league_file_paths[var_league]
        seasons = list(league_paths.keys())
        var_firstseason = int(var_firstseason)
        var_lastseason = int(var_lastseason)
        selected_seasons = [season for season in seasons if var_firstseason <= int(season[-4:]) <= var_lastseason]
        csv_paths = []
        if selected_seasons:
            for season in selected_seasons:
                csv_paths.append(league_paths[season])
            return csv_paths
        else:
            return None
    else:
        return None