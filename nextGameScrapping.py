import logging
import requests
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, List, Optional
import numpy as np
import url

# Configure logging
logging.basicConfig(
   level=logging.INFO,
   format='%(asctime)s - %(levelname)s - %(message)s',
   handlers=[
       #logging.FileHandler('next_game_scraper.log'),
       #logging.StreamHandler()
   ]
)
logger = logging.getLogger(__name__)

class NextGameScraper:
   def __init__(self, api_key: str):
       self.api_key = api_key
       self.league_api_mapping = {
           'Serie A': 'soccer_italy_serie_a',
           'Premier League': 'soccer_epl',
           'La Liga': 'soccer_spain_la_liga', 
           'Bundesliga': 'soccer_germany_bundesliga',
           'Ligue 1': 'soccer_france_ligue_one',
           'Primeira Liga': 'soccer_portugal_primeira_liga'
       }
       
       # Primary bookmakers we prioritize
       self.primary_bookmakers = ['bet365', 'bwin', 'betclic']
       
       # Bookmaker mapping
       self.bookmaker_mapping = {
           'bet365': 'B365',
           'bwin': 'BW',
           'betclic': 'BTC',
           'williamhill': 'WH',
           'pinnacle': 'PS',
           'unibet_eu': 'UN',
           'marathonbet': 'MA',
           'betfair_ex_eu': 'BF',
           'sport888': '888',
           'betsson': 'BS',
           'nordicbet': 'NB',
           'tipico_de': 'TI',
           'coolbet': 'CB',
           'matchbook': 'MB',
           'everygame': 'EG',
           'onexbet': '1X',
           'winamax_fr': 'WM',
           'winamax_de': 'WD',
           'gtbets': 'GT'
       }
       
       # Fallback order
       self.fallback_order = [
           'williamhill', 'pinnacle', 'unibet_eu', 'marathonbet',
           'betfair_ex_eu', 'sport888', 'betsson', 'nordicbet',
           'tipico_de', 'coolbet', 'matchbook', 'everygame',
           'onexbet', 'winamax_fr', 'winamax_de', 'gtbets'
       ]
   
   def get_api_teams(self, league: str) -> dict:
       """Map teams between Football-data.co.uk and The Odds API."""
       api_teams = {}
       
       if league in url.clubs_by_league:
           for team in url.clubs_by_league[league]:
               team_lower = team.lower()
               team_no_spaces = team_lower.replace(' ', '')
               
               api_teams[team_lower] = team
               api_teams[team_no_spaces] = team
               
               # Special cases for Serie A teams
               if team == "Atalanta":
                   api_teams["atalanta bc"] = team
               elif team == "Roma":
                   api_teams["as roma"] = team
               elif team == "Inter":
                   api_teams["inter milan"] = team
               elif team == "Milan":
                   api_teams["ac milan"] = team
       
       return api_teams

   def fetch_odds(self, league: str) -> Optional[List[Dict]]:
       """Fetch odds data from The Odds API for the specified league."""
       sport_key = self.league_api_mapping.get(league, 'soccer_italy_serie_a')
       url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
       
       params = {
           'apiKey': self.api_key,
           'regions': 'eu',
           'markets': 'h2h,totals',
           'oddsFormat': 'decimal',
           'dateFormat': 'iso'
       }
       
       try:
           logger.info(f"Fetching odds for {league} ({sport_key})")
           response = requests.get(url, params=params)
           
           if response.status_code != 200:
               logger.error(f"API Error: {response.text}")
               return None
               
           data = response.json()
           logger.info(f"Fetched {len(data)} events from The Odds API")
           
           # Log available bookmakers
           bookmakers = set()
           for event in data:
               for bookmaker in event.get('bookmakers', []):
                   bookmakers.add(bookmaker.get('key', '').lower())
           
           logger.info(f"Available bookmakers: {', '.join(bookmakers)}")
           return data
       except Exception as e:
           logger.error(f"Error fetching odds data: {str(e)}")
           return None

   def find_match(self, events: List[Dict], star_club: str, opp_club: str, league: str) -> Optional[Dict]:
       """Find the match between two teams in the list of events."""
       if not events:
           logger.error("No events provided to find_match")
           return None
       
       api_teams = self.get_api_teams(league)
       now = datetime.now(timezone.utc)
       
       # Filter current and future matches
       future_events = []
       for event in events:
           try:
               event_time = datetime.fromisoformat(event['commence_time'].replace('Z', '+00:00'))
               if event_time > now or event_time.date() == now.date():
                   future_events.append((event, event_time))
           except (ValueError, KeyError) as e:
               logger.warning(f"Error parsing event time: {e}")
       
       # Sort by start time (closest first)
       future_events.sort(key=lambda x: x[1])
       
       # Special case for Atalanta vs Roma
       if star_club == "Atalanta" and opp_club == "Roma" or star_club == "Roma" and opp_club == "Atalanta":
           for event, _ in future_events:
               home = event.get('home_team', '').lower()
               away = event.get('away_team', '').lower()
               
               if ('atalanta' in home and 'roma' in away) or ('roma' in home and 'atalanta' in away):
                   logger.info(f"Found Atalanta-Roma match: {event.get('home_team')} vs {event.get('away_team')}")
                   return event
       
       star_club_lower = star_club.lower()
       opp_club_lower = opp_club.lower()
       
       # Exact match or known mappings
       for event, _ in future_events:
           home_team = event.get('home_team', '').lower()
           away_team = event.get('away_team', '').lower()
           
           # Check both directions
           if ((home_team == star_club_lower or home_team in api_teams.get(star_club_lower, [])) and 
               (away_team == opp_club_lower or away_team in api_teams.get(opp_club_lower, []))):
               logger.info(f"Found match: {event.get('home_team')} vs {event.get('away_team')}")
               return event
           
           if ((home_team == opp_club_lower or home_team in api_teams.get(opp_club_lower, [])) and 
               (away_team == star_club_lower or away_team in api_teams.get(star_club_lower, []))):
               logger.info(f"Found match (reversed): {event.get('home_team')} vs {event.get('away_team')}")
               return event
       
       # Substring matching as fallback
       for event, _ in future_events:
           home_team = event.get('home_team', '').lower()
           away_team = event.get('away_team', '').lower()
           
           if ((star_club_lower in home_team or home_team in star_club_lower) and 
               (opp_club_lower in away_team or away_team in opp_club_lower)):
               logger.info(f"Found match (substring): {event.get('home_team')} vs {event.get('away_team')}")
               return event
           
           if ((star_club_lower in away_team or away_team in star_club_lower) and 
               (opp_club_lower in home_team or home_team in opp_club_lower)):
               logger.info(f"Found match (substring reversed): {event.get('home_team')} vs {event.get('away_team')}")
               return event
       
       logger.warning(f"No match found for {star_club} vs {opp_club}")
       return None

   def map_bookmakers(self, event: Dict) -> Dict[str, Dict[str, str]]:
       """Map available bookmakers to our preferred format."""
       bookmakers_with_1x2 = set()
       bookmakers_with_totals = set()
       
       for bookmaker in event.get('bookmakers', []):
           key = bookmaker.get('key', '').lower()
           if not key:
               continue
           
           # Check which markets this bookmaker provides
           for market in bookmaker.get('markets', []):
               market_key = market.get('key', '')
               if market_key == 'h2h':
                   bookmakers_with_1x2.add(key)
               elif market_key == 'totals':
                   for outcome in market.get('outcomes', []):
                       if outcome.get('point') == 2.5:
                           bookmakers_with_totals.add(key)
                           break
       
       logger.info(f"Bookmakers with 1X2 odds: {', '.join(bookmakers_with_1x2)}")
       logger.info(f"Bookmakers with totals (2.5) odds: {', '.join(bookmakers_with_totals)}")
       
       # Handle 1X2 mapping
       h2h_mapping = {}
       for primary in self.primary_bookmakers:
           if primary in bookmakers_with_1x2:
               h2h_mapping[primary] = primary
           else:
               for fallback in self.fallback_order:
                   if fallback in bookmakers_with_1x2 and fallback not in h2h_mapping.values():
                       h2h_mapping[primary] = fallback
                       logger.info(f"Using {fallback} as substitute for {primary} (1X2 odds)")
                       break
       
       # Handle totals mapping
       totals_mapping = {}
       for primary in self.primary_bookmakers:
           if primary in bookmakers_with_totals:
               totals_mapping[primary] = primary
           else:
               for fallback in self.fallback_order:
                   if fallback in bookmakers_with_totals and fallback not in totals_mapping.values():
                       totals_mapping[primary] = fallback
                       logger.info(f"Using {fallback} as substitute for {primary} (totals odds)")
                       break
       
       return {
           '1x2': h2h_mapping,
           'totals': totals_mapping
       }

   def process_1x2_odds(self, event: Dict) -> Dict[str, str]:
       """Process 1X2 odds from available bookmakers, prioritizing any valid odds."""
       odds_data = {
           'MaxH': '0', 'MaxD': '0', 'MaxA': '0',
           'AvgH': '0', 'AvgD': '0', 'AvgA': '0'
       }
       
       if not event or 'bookmakers' not in event:
           logger.error("No bookmakers data in event")
           return odds_data
       
       # Collect all odds for max/avg calculations
       home_odds = []
       draw_odds = []
       away_odds = []
       h2h_bookmakers = []
       
       # Gather all bookmakers with valid 1X2 odds
       for bookmaker in event.get('bookmakers', []):
           bookmaker_key = bookmaker.get('key', '').lower()
           for market in bookmaker.get('markets', []):
               if market.get('key') != 'h2h':
                   continue
               outcomes = {outcome.get('name', '').lower(): outcome.get('price')
                          for outcome in market.get('outcomes', [])}
               home = outcomes.get(event.get('home_team', '').lower(), outcomes.get('home', ''))
               draw = outcomes.get('draw', '')
               away = outcomes.get(event.get('away_team', '').lower(), outcomes.get('away', ''))
               if home and draw and away:
                   try:
                       home_val = float(home)
                       draw_val = float(draw)
                       away_val = float(away)
                       h2h_bookmakers.append({
                           'key': bookmaker_key,
                           'home': home_val,
                           'draw': draw_val,
                           'away': away_val
                       })
                       home_odds.append(home_val)
                       draw_odds.append(draw_val)
                       away_odds.append(away_val)
                   except (ValueError, TypeError) as e:
                       logger.warning(f"Invalid odds for {bookmaker_key}: {e}")
       
       logger.info(f"Found 1X2 odds from {len(h2h_bookmakers)} bookmakers")
       
       # Map bookmakers to preferred codes
       bookmaker_mapping = self.map_bookmakers(event)['1x2']
       used_bookmakers = set()
       
       # First, try to assign preferred bookmakers
       for primary, actual_bookie in bookmaker_mapping.items():
           code = self.bookmaker_mapping.get(primary)
           if not code:
               continue
           for bookie_data in h2h_bookmakers:
               if bookie_data['key'] == actual_bookie and actual_bookie not in used_bookmakers:
                   odds_data[f'{code}H'] = str(bookie_data['home'])
                   odds_data[f'{code}D'] = str(bookie_data['draw'])
                   odds_data[f'{code}A'] = str(bookie_data['away'])
                   logger.info(f"Assigned {actual_bookie} odds to {code}: H={bookie_data['home']}, D={bookie_data['draw']}, A={bookie_data['away']}")
                   used_bookmakers.add(actual_bookie)
                   break
       
       # Fill any remaining slots with available bookmakers
       for bookie_data in h2h_bookmakers:
           if bookie_data['key'] in used_bookmakers:
               continue
           code = self.bookmaker_mapping.get(bookie_data['key'], bookie_data['key'][:2].upper())
           if code not in odds_data:
               odds_data[f'{code}H'] = str(bookie_data['home'])
               odds_data[f'{code}D'] = str(bookie_data['draw'])
               odds_data[f'{code}A'] = str(bookie_data['away'])
               logger.info(f"Assigned {bookie_data['key']} odds to {code}: H={bookie_data['home']}, D={bookie_data['draw']}, A={bookie_data['away']}")
               used_bookmakers.add(bookie_data['key'])
       
       # Calculate max and average odds
       if home_odds:
           odds_data['MaxH'] = str(max(home_odds))
           odds_data['AvgH'] = str(round(np.mean(home_odds), 2))
       if draw_odds:
           odds_data['MaxD'] = str(max(draw_odds))
           odds_data['AvgD'] = str(round(np.mean(draw_odds), 2))
       if away_odds:
           odds_data['MaxA'] = str(max(away_odds))
           odds_data['AvgA'] = str(round(np.mean(away_odds), 2))
       
       return odds_data

   def process_goals_odds(self, event: Dict) -> Dict[str, str]:
       """Process over/under 2.5 goals odds."""
       odds_data = {}
       
       if not event or 'bookmakers' not in event:
           return odds_data
           
       over_odds = []
       under_odds = []
       
       bookmaker_mapping = self.map_bookmakers(event)
       totals_mapping = bookmaker_mapping['totals']
       
       bookmaker_totals = {}
       for bookmaker in event.get('bookmakers', []):
           bookmaker_key = bookmaker.get('key', '').lower()
           for market in bookmaker.get('markets', []):
               if market.get('key') != 'totals':
                   continue
               for outcome in market.get('outcomes', []):
                   point = outcome.get('point')
                   if point != 2.5:
                       continue
                   name = outcome.get('name', '').lower()
                   price = outcome.get('price')
                   if not name or not price:
                       continue
                   if bookmaker_key not in bookmaker_totals:
                       bookmaker_totals[bookmaker_key] = {'over': None, 'under': None}
                   if name == 'over':
                       bookmaker_totals[bookmaker_key]['over'] = float(price)
                   elif name == 'under':
                       bookmaker_totals[bookmaker_key]['under'] = float(price)
       
       to_remove = []
       for bookie, odds in bookmaker_totals.items():
           if odds['over'] is None or odds['under'] is None:
               to_remove.append(bookie)
           else:
               over_odds.append(odds['over'])
               under_odds.append(odds['under'])
               
       for bookie in to_remove:
           del bookmaker_totals[bookie]
           
       logger.info(f"Collected goals odds from {len(bookmaker_totals)} bookmakers")
       
       for primary, actual_bookie in totals_mapping.items():
           if actual_bookie in bookmaker_totals:
               code = self.bookmaker_mapping.get(primary)
               if not code:
                   continue
               odds = bookmaker_totals[actual_bookie]
               odds_data[f'{code}>2.5'] = str(odds['over'])
               odds_data[f'{code}<2.5'] = str(odds['under'])
               logger.info(f"Using {actual_bookie} odds for {code} >2.5/<2.5: {odds['over']}/{odds['under']}")
       
       if over_odds:
           odds_data['Max>2.5'] = str(max(over_odds))
           odds_data['Avg>2.5'] = str(round(np.mean(over_odds), 2))
       if under_odds:
           odds_data['Max<2.5'] = str(max(under_odds))
           odds_data['Avg<2.5'] = str(round(np.mean(under_odds), 2))
       
       return odds_data

   def save_to_csv(self, event: Dict, odds_1x2: Dict, odds_goals: Dict):
    """Save match data to nextGame.csv with columns matching historical data."""
    try:
        home_team = event.get('home_team', 'Unknown')
        away_team = event.get('away_team', 'Unknown')
        commence_time = event.get('commence_time', '')

        # Process date to match treatment_of_date
        date_str = ''
        week_day = ''
        day = 0
        month = 0
        year = 0

        try:
            match_date = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
            date_str = match_date.strftime('%Y-%m-%d')  # Format as YYYY-MM-DD
            week_day = match_date.strftime('%A')
            day = match_date.day
            month = match_date.month
            year = match_date.year
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing commence_time {commence_time}: {e}")
            date_str = commence_time
            week_day = 'Unknown'

        # Define columns to match test dataset (excluding targets and feedback)
        columns = [
            'HomeTeam', 'AwayTeam',  'Day_of_week', 'Day', 'Month', 'Year',
            'B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA',
            'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA',
            'B365>2.5', 'B365<2.5', 'Max>2.5', 'Max<2.5', 'Avg>2.5', 'Avg<2.5'
        ]

        # Initialize row with default values
        row = {col: '0' for col in columns}
        row.update({
            'HomeTeam': home_team,
            'AwayTeam': away_team,
            #'Date': date_str,
            'WeekDay': week_day,
            'Day': day,
            'Month': month,
            'Year': year
        })

        # Update with 1X2 odds
        for key in ['B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA', 'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA']:
            if key in odds_1x2:
                row[key] = str(odds_1x2[key])

        # Update with goals odds
        for key in ['B365>2.5', 'B365<2.5', 'Max>2.5', 'Max<2.5', 'Avg>2.5', 'Avg<2.5']:
            if key in odds_goals:
                row[key] = str(odds_goals[key])

        # Create DataFrame and save to CSV
        df = pd.DataFrame([row], columns=columns)
        df.to_csv('NextGame.csv', index=False)
        logger.info("Successfully saved match data to NextGame.csv with columns: %s", columns)

    except Exception as e:
        logger.error(f"Error saving CSV: {str(e)}")

   def get_next_game_data(self, odds_url: str, star_club: str, opp_club: str, game_date: str, league: str = "La Liga") -> Dict[str, str]:
       """Fetch 1X2 odds for the next game."""
       logger.info(f"Getting odds for {star_club} vs {opp_club} in {league}")
       
       events = self.fetch_odds(league)
       if not events:
           logger.error("No events fetched from API")
           return {
               'B365H': '0', 'B365D': '0', 'B365A': '0',
               'BWH': '0', 'BWD': '0', 'BWA': '0',
               'BTCH': '0', 'BTCD': '0', 'BTCA': '0',
               'MaxH': '0', 'MaxD': '0', 'MaxA': '0',
               'AvgH': '0', 'AvgD': '0', 'AvgA': '0',
               'error': 'No events fetched from API'
           }

       event = self.find_match(events, star_club, opp_club, league)
       if not event:
           logger.error(f"Match not found for {star_club} vs {opp_club}")
           return {
               'B365H': '0', 'B365D': '0', 'B365A': '0',
               'BWH': '0', 'BWD': '0', 'BWA': '0',
               'BTCH': '0', 'BTCD': '0', 'BTCA': '0',
               'MaxH': '0', 'MaxD': '0', 'MaxA': '0',
               'AvgH': '0', 'AvgD': '0', 'AvgA': '0',
               'error': f'Match not found for {star_club} vs {opp_club}'
           }

       odds_data = self.process_1x2_odds(event)
       return odds_data

   def get_next_game_goals_data(self, odds_url: str, star_club: str, opp_club: str, game_date: str, league: str = "Serie A") -> Dict[str, str]:
       """Fetch over/under 2.5 goals odds for the next game and save to CSV."""
       logger.info(f"Getting goals odds for {star_club} vs {opp_club} in {league}")
       
       events = self.fetch_odds(league)
       if not events:
           logger.error("No events fetched from API")
           return {
               'B365>2.5': '0', 'B365<2.5': '0',
               'BW>2.5': '0', 'BW<2.5': '0',
               'BTC>2.5': '0', 'BTC<2.5': '0',
               'Max>2.5': '0', 'Max<2.5': '0',
               'Avg>2.5': '0', 'Avg<2.5': '0',
               'error': 'No events fetched from API'
           }

       event = self.find_match(events, star_club, opp_club, league)
       if not event:
           logger.error(f"Match not found for {star_club} vs {opp_club}")
           return {
               'B365>2.5': '0', 'B365<2.5': '0',
               'BW>2.5': '0', 'BW<2.5': '0',
               'BTC>2.5': '0', 'BTC<2.5': '0',
               'Max>2.5': '0', 'Max<2.5': '0',
               'Avg>2.5': '0', 'Avg<2.5': '0',
               'error': f'Match not found for {star_club} vs {opp_club}'
           }

       goals_data = self.process_goals_odds(event)
       odds_1x2 = self.process_1x2_odds(event)
       self.save_to_csv(event, odds_1x2, goals_data)
       
       return goals_data

# Singleton instance
_SCRAPER_INSTANCE = None

def get_scraper(api_key: str = "6521a8f852098babe8777208742ae518"):
   """Get or create a singleton instance of the NextGameScraper."""
   global _SCRAPER_INSTANCE
   if _SCRAPER_INSTANCE is None:
       _SCRAPER_INSTANCE = NextGameScraper(api_key)
   return _SCRAPER_INSTANCE



def get_next_game_data(odds_url: str, star_club: str = None, opp_club: str = None, game_date: str = None, league: str = "Serie A") -> Dict[str, str]:
   """Fetch 1X2 odds for the next game."""
   # Check if any of the parameters is None and log it
   if star_club is None or opp_club is None or game_date is None or league is None:
       logger.warning(f"Missing parameters: star_club={star_club}, opp_club={opp_club}, game_date={game_date}, league={league}")
       if game_date is None:
           game_date = datetime.now().strftime("%d/%m/%Y")  # Default to today

   scraper = get_scraper()
   return scraper.get_next_game_data(odds_url, star_club, opp_club, game_date, league)

def get_next_game_goals_data(odds_url: str, star_club: str = None, opp_club: str = None, game_date: str = None, league: str = "Serie A") -> Dict[str, str]:
   """Fetch over/under 2.5 goals odds for the next game and save to CSV."""
   # Check if any of the parameters is None and log it
   if star_club is None or opp_club is None or game_date is None or league is None:
       logger.warning(f"Missing parameters: star_club={star_club}, opp_club={opp_club}, game_date={game_date}, league={league}")
       if game_date is None:
           game_date = datetime.now().strftime("%d/%m/%Y")  # Default to today
   
   scraper = get_scraper()
   return scraper.get_next_game_goals_data(odds_url, star_club, opp_club, game_date, league)