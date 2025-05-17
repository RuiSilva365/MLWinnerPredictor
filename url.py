# url.py
# Mapping of local league and club names to data source URLs and utility functions
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
# Club to city mapping for weather data (latitude, longitude)
club_to_city = {
    # Serie A
    'Atalanta': {'city': 'Bergamo', 'lat': 45.6983, 'lon': 9.6673},
    'Bologna': {'city': 'Bologna', 'lat': 44.4949, 'lon': 11.3426},
    'Cagliari': {'city': 'Cagliari', 'lat': 39.2238, 'lon': 9.1217},
    'Como': {'city': 'Como', 'lat': 45.8081, 'lon': 9.0852},
    'Empoli': {'city': 'Empoli', 'lat': 43.7259, 'lon': 10.9522},
    'Fiorentina': {'city': 'Florence', 'lat': 43.7696, 'lon': 11.2558},
    'Genoa': {'city': 'Genoa', 'lat': 44.4056, 'lon': 8.9463},
    'Inter': {'city': 'Milan', 'lat': 45.4642, 'lon': 9.1900},
    'Juventus': {'city': 'Turin', 'lat': 45.0703, 'lon': 7.6869},
    'Lazio': {'city': 'Rome', 'lat': 41.9028, 'lon': 12.4964},
    'Lecce': {'city': 'Lecce', 'lat': 40.3515, 'lon': 18.1740},
    'Milan': {'city': 'Milan', 'lat': 45.4642, 'lon': 9.1900},
    'Monza': {'city': 'Monza', 'lat': 45.5845, 'lon': 9.2749},
    'Napoli': {'city': 'Naples', 'lat': 40.8518, 'lon': 14.2681},
    'Parma': {'city': 'Parma', 'lat': 44.8015, 'lon': 10.3280},
    'Roma': {'city': 'Rome', 'lat': 41.9028, 'lon': 12.4964},
    'Torino': {'city': 'Turin', 'lat': 45.0703, 'lon': 7.6869},
    'Udinese': {'city': 'Udine', 'lat': 46.0604, 'lon': 13.2346},
    'Venezia': {'city': 'Venice', 'lat': 45.4408, 'lon': 12.3155},
    'Verona': {'city': 'Verona', 'lat': 45.4384, 'lon': 10.9916},
    # Primeira Liga (example)
    'Sp Lisbon': {'city': 'Lisbon', 'lat': 38.7223, 'lon': -9.1393},
    'Benfica': {'city': 'Lisbon', 'lat': 38.7223, 'lon': -9.1393},
    'Porto': {'city': 'Porto', 'lat': 41.1579, 'lon': -8.6291},
}

club_to_fixture_names = {
    # Premier League
    "Arsenal": ["Arsenal"],
    "Aston Villa": ["Aston Villa"],
    "Bournemouth": ["Bournemouth"],
    "Brentford": ["Brentford"],
    "Brighton": ["Brighton", "Brighton & Hove Albion"],
    "Chelsea": ["Chelsea"],
    "Crystal Palace": ["Crystal Palace"],
    "Everton": ["Everton"],
    "Fulham": ["Fulham"],
    "Ipswich": ["Ipswich", "Ipswich Town"],
    "Leicester": ["Leicester", "Leicester City"],
    "Liverpool": ["Liverpool"],
    "Man City": ["Man City", "Manchester City"],
    "Man United": ["Man United", "Manchester United"],
    "Newcastle": ["Newcastle", "Newcastle United"],
    "Nott'm Forest": ["Nottingham Forest", "Nott'm Forest"],
    "Southampton": ["Southampton"],
    "Tottenham": ["Tottenham", "Tottenham Hotspur"],
    "West Ham": ["West Ham", "West Ham United"],
    "Wolves": ["Wolves", "Wolverhampton Wanderers"],
    
    # Serie A
    "Atalanta": ["Atalanta", "Atalanta BC"],
    "Bologna": ["Bologna"],
    "Cagliari": ["Cagliari"],
    "Como": ["Como"],
    "Empoli": ["Empoli"],
    "Fiorentina": ["Fiorentina"],
    "Genoa": ["Genoa"],
    "Inter": ["Inter", "Inter Milan"],
    "Juventus": ["Juventus", "Juventus FC"],
    "Lazio": ["Lazio"],
    "Lecce": ["Lecce"],
    "Milan": ["Milan", "AC Milan"],
    "Monza": ["Monza"],
    "Napoli": ["Napoli"],
    "Parma": ["Parma"],
    "Roma": ["Roma", "AS Roma"],
    "Torino": ["Torino"],
    "Udinese": ["Udinese"],
    "Venezia": ["Venezia"],
    "Verona": ["Verona", "Hellas Verona"],
    
    # Add other leagues as needed
    # La Liga
    "Barcelona": ["Barcelona", "FC Barcelona"],
    "Real Madrid": ["Real Madrid"],
    "Ath Madrid": ["Atletico Madrid", "Atlético Madrid", "Ath Madrid"],
    "Sevilla": ["Sevilla", "Sevilla FC"],
    
    # Bundesliga
    "Bayern Munich": ["Bayern Munich", "Bayern München"],
    "Dortmund": ["Dortmund", "Borussia Dortmund"],
    "Leverkusen": ["Leverkusen", "Bayer Leverkusen"],
    
    # Primeira Liga
    "Benfica": ["Benfica", "SL Benfica"],
    "Porto": ["Porto", "FC Porto"],
    "Sp Lisbon": ["Sporting CP", "Sporting Lisbon", "Sp Lisbon"],
    
    # Ligue 1
    "Paris SG": ["Paris SG", "Paris Saint-Germain", "PSG"]
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

# Mapping of league names to their corresponding fixture URLs
league_to_fixtures_url = {
    "Premier League": "https://www.soccerstats.com/results.asp?league=england",
    "Bundesliga": "https://www.soccerstats.com/results.asp?league=germany",
    "La Liga": "https://www.soccerstats.com/results.asp?league=spain",
    "Serie A": "https://www.soccerstats.com/results.asp?league=italy",
    "Primeira Liga": "https://www.soccerstats.com/results.asp?league=portugal",
    "Ligue 1": "https://www.soccerstats.com/results.asp?league=france"
}

# Match local club names to names used in fixture websites
club_to_fixture_names = {
    # Premier League
    "Arsenal": ["Arsenal"],
    "Aston Villa": ["Aston Villa"],
    "Bournemouth": ["Bournemouth"],
    "Brentford": ["Brentford"],
    "Brighton": ["Brighton", "Brighton & Hove Albion"],
    "Chelsea": ["Chelsea"],
    "Crystal Palace": ["Crystal Palace"],
    "Everton": ["Everton"],
    "Fulham": ["Fulham"],
    "Ipswich": ["Ipswich", "Ipswich Town"],
    "Leicester": ["Leicester", "Leicester City"],
    "Liverpool": ["Liverpool"],
    "Man City": ["Man City", "Manchester City"],
    "Man United": ["Man United", "Manchester United"],
    "Newcastle": ["Newcastle", "Newcastle United"],
    "Nott'm Forest": ["Nottingham Forest", "Nott'm Forest"],
    "Southampton": ["Southampton"],
    "Tottenham": ["Tottenham", "Tottenham Hotspur"],
    "West Ham": ["West Ham", "West Ham United"],
    "Wolves": ["Wolves", "Wolverhampton Wanderers"],
    # Serie A
    "Atalanta": ["Atalanta", "Atalanta BC"],
    "Bologna": ["Bologna"],
    "Cagliari": ["Cagliari"],
    "Como": ["Como"],
    "Empoli": ["Empoli"],
    "Fiorentina": ["Fiorentina"],
    "Genoa": ["Genoa"],
    "Inter": ["Inter", "Inter Milan"],
    "Juventus": ["Juventus", "Juventus FC"],
    "Lazio": ["Lazio"],
    "Lecce": ["Lecce"],
    "Milan": ["Milan", "AC Milan"],
    "Monza": ["Monza"],
    "Napoli": ["Napoli"],
    "Parma": ["Parma"],
    "Roma": ["Roma", "AS Roma"],
    "Torino": ["Torino"],
    "Udinese": ["Udinese"],
    "Venezia": ["Venezia"],
    "Verona": ["Verona", "Hellas Verona"],
    # Other leagues
    "Barcelona": ["Barcelona", "FC Barcelona"],
    "Real Madrid": ["Real Madrid"],
    "Ath Madrid": ["Atletico Madrid", "Atlético Madrid", "Ath Madrid"],
    "Sevilla": ["Sevilla", "Sevilla FC"],
    "Bayern Munich": ["Bayern Munich", "Bayern München"],
    "Dortmund": ["Dortmund", "Borussia Dortmund"],
    "Leverkusen": ["Leverkusen", "Bayer Leverkusen"],
    "Benfica": ["Benfica", "SL Benfica"],
    "Porto": ["Porto", "FC Porto"],
    "Sp Lisbon": ["Sporting CP", "Sporting Lisbon", "Sp Lisbon"],
    "Paris SG": ["Paris SG", "Paris Saint-Germain", "PSG"]
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
    "Verona": "Hellas Verona"
}

def file_path_builder(var_league: str, var_firstseason: int, var_lastseason: int) -> list:
    """Build a list of CSV file paths for a given league and season range."""
    league_codes = {
        "Premier League": "E0",
        "Bundesliga": "D1",
        "La Liga": "SP1",
        "Serie A": "I1",
        "Primeira Liga": "P1",
        "Ligue 1": "F1"
    }
    
    if var_league not in league_codes:
        logger.error(f"League {var_league} not supported")
        raise ValueError(f"League {var_league} not supported")
    
    season_str = f"{var_firstseason % 100:02d}{(var_lastseason + 1) % 100:02d}"
    url = f"https://www.football-data.co.uk/mmz4281/{season_str}/{league_codes[var_league]}.csv"
    return [url]

def club_match_in_fixture(team_name: str, fixture_name: str) -> bool:
    """Check if a team name matches a fixture name."""
    if team_name in club_to_fixture_names:
        return any(alt_name.lower() in fixture_name.lower() for alt_name in club_to_fixture_names[team_name])
    return False

def fetch_upcoming_fixtures(league: str) -> list:
    """Fetch upcoming fixtures for a given league."""
    if league not in league_to_fixtures_url:
        logger.error(f"League {league} not supported")
        raise ValueError(f"League {league} not supported")
    
    url = league_to_fixtures_url[league]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        fixtures = []
        current_date = datetime.now()
        
        fixture_tables = soup.find_all('table', {'class': ['scores', 'schedule']})
        for table in fixture_tables:
            date_header = None
            previous_element = table.find_previous(['h2', 'h3', 'h4'])
            if previous_element:
                date_text = previous_element.get_text().strip()
                date_match = re.search(r'\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b', date_text)
                if date_match:
                    try:
                        date_header = datetime.strptime(date_match.group(0), '%d/%m/%Y')
                    except ValueError:
                        pass
                if not date_header:
                    try:
                        date_header = datetime.strptime(date_text, '%A, %B %d, %Y')
                    except ValueError:
                        try:
                            date_header = datetime.strptime(date_text, '%d %B %Y')
                        except ValueError:
                            date_header = current_date
            
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 5:
                    try:
                        time_cell = cells[0].get_text().strip()
                        home_team = cells[1].get_text().strip()
                        score_cell = cells[2].get_text().strip()
                        away_team = cells[3].get_text().strip()
                        
                        if not re.match(r'\d+\s*-\s*\d+', score_cell) and home_team and away_team:
                            fixture_date = date_header.strftime('%d/%m/%Y') if date_header else current_date.strftime('%d/%m/%Y')
                            fixtures.append({
                                'date': fixture_date,
                                'time': time_cell,
                                'home_team': home_team,
                                'away_team': away_team
                            })
                    except Exception as e:
                        logger.warning(f"Error processing fixture row: {e}")
                        continue
        
        return fixtures
    
    except Exception as e:
        logger.error(f"Error fetching fixtures for {league}: {str(e)}")
        raise

def find_next_game(star_club: str, opp_club: str, league: str, custom_date: str = None) -> dict:
    """Find the next game between two specified clubs."""
    try:
        fixtures = fetch_upcoming_fixtures(league)
        for fixture in fixtures:
            home_match = club_match_in_fixture(star_club, fixture['home_team'])
            away_match = club_match_in_fixture(star_club, fixture['away_team'])
            
            if home_match and club_match_in_fixture(opp_club, fixture['away_team']):
                return {
                    'date': fixture['date'],
                    'home_team': fixture['home_team'],
                    'away_team': fixture['away_team'],
                    'is_star_club_home': True
                }
            elif away_match and club_match_in_fixture(opp_club, fixture['home_team']):
                return {
                    'date': fixture['date'],
                    'home_team': fixture['home_team'],
                    'away_team': fixture['away_team'],
                    'is_star_club_home': False
                }
        
        if custom_date:
            is_star_club_home = bool(hash(star_club) % 2)
            return {
                'date': custom_date,
                'home_team': star_club if is_star_club_home else opp_club,
                'away_team': opp_club if is_star_club_home else star_club,
                'is_star_club_home': is_star_club_home
            }
        
        raise ValueError(f"No upcoming game found for {star_club} vs {opp_club}")
    
    except Exception as e:
        logger.error(f"Error finding next game: {str(e)}")
        raise