import logging
import requests
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import sys
import numpy as np
import url
import difflib


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
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
        self.primary_bookmakers = ['bet365', 'bwin', 'betclic']
        self.bookmaker_mapping = {
            'bet365': 'B365', 'bwin': 'BW', 'betclic': 'BTC', 'williamhill': 'WH',
            'pinnacle': 'PS', 'unibet_eu': 'UN', 'marathonbet': 'MA', 'betfair_ex_eu': 'BF',
            'sport888': '888', 'betsson': 'BS', 'nordicbet': 'NB', 'tipico_de': 'TI',
            'coolbet': 'CB', 'matchbook': 'MB', 'everygame': 'EG', 'onexbet': '1X',
            'winamax_fr': 'WM', 'winamax_de': 'WD', 'gtbets': 'GT'
        }
        self.fallback_order = [
            'williamhill', 'pinnacle', 'unibet_eu', 'marathonbet', 'betfair_ex_eu',
            'sport888', 'betsson', 'nordicbet', 'tipico_de', 'coolbet', 'matchbook',
            'everygame', 'onexbet', 'winamax_fr', 'winamax_de', 'gtbets'
        ]

    def fetch_odds(self, league: str) -> Optional[List[Dict]]:
        """Fetch odds data from The Odds API for the specified league."""
        sport_key = self.league_api_mapping.get(league, 'soccer_italy_serie_a')
        api_url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
        params = {
            'apiKey': self.api_key,
            'regions': 'eu',
            'markets': 'h2h,totals',
            'oddsFormat': 'decimal',
            'dateFormat': 'iso'
        }
        try:
            logger.info(f"Fetching odds for {league} ({sport_key})")
            response = requests.get(api_url, params=params)
            if response.status_code != 200:
                logger.error(f"API Error: {response.text}")
                return None
            data = response.json()
            logger.info(f"Fetched {len(data)} events from The Odds API")
            bookmakers = set()
            for event in data:
                for bookmaker in event.get('bookmakers', []):
                    bookmakers.add(bookmaker.get('key', '').lower())
            logger.info(f"Available bookmakers: {', '.join(bookmakers)}")
            return data
        except Exception as e:
            logger.error(f"Error fetching odds data: {str(e)}")
            return None

    def list_upcoming_games(self, events: List[Dict], league: str) -> List[Tuple[Dict, str]]:
        """List upcoming games for the league, returning events with display strings."""
        if not events:
            logger.error("No events provided to list_upcoming_games")
            return []
        
        now = datetime.now(timezone.utc)
        future_events = []
        for event in events:
            try:
                event_time = datetime.fromisoformat(event['commence_time'].replace('Z', '+00:00'))
                if event_time >= now or event_time.date() == now.date():
                    display_str = f"{event.get('home_team', 'Unknown')} vs {event.get('away_team', 'Unknown')} at {event_time.strftime('%Y-%m-%d %H:%M UTC')}"
                    future_events.append((event, display_str))
            except (ValueError, KeyError) as e:
                logger.warning(f"Error parsing event time: {e}")
        
        future_events.sort(key=lambda x: x[0]['commence_time'])
        logger.info(f"Found {len(future_events)} upcoming games for {league}")
        return future_events


    def find_match(self, events: List[Dict], star_club: str, opp_club: str, league: str, game_date: str = None) -> Optional[Dict]:
        """Find the match between two teams, with fallback to default selection if not found."""
        if not events:
            logger.error("No events provided to find_match")
            return None
        
        # Map local club names to Odds API names
        star_club_api = url.club_to_odds_api.get(star_club, star_club)
        opp_club_api = url.club_to_odds_api.get(opp_club, opp_club)
        now = datetime.now(timezone.utc)
        
        logger.info(f"Searching for match: {star_club} ({star_club_api}) vs {opp_club} ({opp_club_api}) in {league}")
        
        # Parse game_date if provided (format: DD/MM/YYYY)
        target_date = None
        if game_date:
            try:
                target_date = datetime.strptime(game_date, "%d/%m/%Y").date()
                logger.info(f"Filtering for game date: {target_date}")
            except ValueError:
                logger.warning(f"Invalid game_date format: {game_date}. Ignoring date filter.")
        
        # Filter current and future matches
        future_events = []
        for event in events:
            try:
                event_time = datetime.fromisoformat(event['commence_time'].replace('Z', '+00:00'))
                event_date = event_time.date()
                if (event_time >= now or event_date == now.date()) and (not target_date or event_date == target_date):
                    future_events.append((event, event_time))
            except (ValueError, KeyError) as e:
                logger.warning(f"Error parsing event time: {e}")
        
        future_events.sort(key=lambda x: x[1])
        logger.info(f"Found {len(future_events)} future or current events")
        
        # Exact match using Odds API names
        for event, _ in future_events:
            home_team = event.get('home_team', '').lower()
            away_team = event.get('away_team', '').lower()
            star_club_api_lower = star_club_api.lower()
            opp_club_api_lower = opp_club_api.lower()
            
            if (home_team == star_club_api_lower and away_team == opp_club_api_lower) or \
            (home_team == opp_club_api_lower and away_team == star_club_api_lower):
                logger.info(f"Found exact match: {event.get('home_team')} vs {event.get('away_team')}")
                return event
        
        # Fuzzy matching with a lower threshold
        best_match = None
        best_score = 0.0
        for event, _ in future_events:
            home_team = event.get('home_team', '').lower()
            away_team = event.get('away_team', '').lower()
            star_similarity = max(
                difflib.SequenceMatcher(None, star_club_api_lower, home_team).ratio(),
                difflib.SequenceMatcher(None, star_club_api_lower, away_team).ratio()
            )
            opp_similarity = max(
                difflib.SequenceMatcher(None, opp_club_api_lower, home_team).ratio(),
                difflib.SequenceMatcher(None, opp_club_api_lower, away_team).ratio()
            )
            combined_score = min(star_similarity, opp_similarity)
            if combined_score > 0.7 and combined_score > best_score:
                best_match = event
                best_score = combined_score
        
        if best_match:
            logger.info(f"Found fuzzy match: {best_match.get('home_team')} vs {best_match.get('away_team')} "
                        f"(Similarity score: {best_score:.2f})")
            return best_match
        
        # Fallback: List upcoming games and handle selection
        logger.warning(f"No match found for {star_club} vs {opp_club}. Listing upcoming games.")
        upcoming_games = self.list_upcoming_games(events, league)
        if not upcoming_games:
            logger.error("No upcoming games available for selection")
            logger.error(f"No upcoming games available for {league}")
            return None
        
        # Non-interactive environment: Default to first game
        if not sys.stdin.isatty():
            logger.info("Non-interactive environment: Defaulting to first available game")
            selected_event, _ = upcoming_games[0]
            logger.info(f"Selected game: {selected_event.get('home_team')} vs {selected_event.get('away_team')}")
            return selected_event
        
        # Interactive environment: Prompt for selection
        print(f"\nNo exact match found for {star_club} vs {opp_club} in {league}.")
        print("Please select an upcoming game:")
        for i, (_, display_str) in enumerate(upcoming_games, 1):
            print(f"  {i}. {display_str}")
        
        while True:
            try:
                selection = input("Insert game number: ").strip()
                idx = int(selection) - 1
                if 0 <= idx < len(upcoming_games):
                    selected_event, _ = upcoming_games[idx]
                    logger.info(f"User selected game: {selected_event.get('home_team')} vs {selected_event.get('away_team')}")
                    return selected_event
                print(f"Invalid number. Please enter a number between 1 and {len(upcoming_games)}")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def map_bookmakers(self, event: Dict) -> Dict[str, Dict[str, str]]:
        """Map available bookmakers to our preferred format."""
        bookmakers_with_1x2 = set()
        bookmakers_with_totals = set()
        
        for bookmaker in event.get('bookmakers', []):
            key = bookmaker.get('key', '').lower()
            if not key:
                continue
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
        
        return {'1x2': h2h_mapping, 'totals': totals_mapping}

    def process_1x2_odds(self, event: Dict) -> Dict[str, str]:
        """Process 1X2 odds from available bookmakers."""
        odds_data = {
            'MaxH': '0', 'MaxD': '0', 'MaxA': '0',
            'AvgH': '0', 'AvgD': '0', 'AvgA': '0'
        }
        
        if not event or 'bookmakers' not in event:
            logger.error("No bookmakers data in event")
            return odds_data
        
        home_odds = []
        draw_odds = []
        away_odds = []
        h2h_bookmakers = []
        
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
        
        bookmaker_mapping = self.map_bookmakers(event)['1x2']
        used_bookmakers = set()
        
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
        """Save match data to NextGame.csv with columns matching historical data."""
        try:
            home_team = event.get('home_team', 'Unknown')
            away_team = event.get('away_team', 'Unknown')
            commence_time = event.get('commence_time', '')
            date_str = ''
            week_day = ''
            day = 0
            month = 0
            year = 0
            try:
                match_date = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
                date_str = match_date.strftime('%Y-%m-%d')
                week_day = match_date.strftime('%A')
                day = match_date.day
                month = match_date.month
                year = match_date.year
            except (ValueError, TypeError) as e:
                logger.error(f"Error parsing commence_time {commence_time}: {e}")
                date_str = commence_time
                week_day = 'Unknown'
            
            columns = [
                'HomeTeam', 'AwayTeam', 'Day_of_week', 'Day', 'Month', 'Year',
                'B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA',
                'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA',
                'B365>2.5', 'B365<2.5', 'Max>2.5', 'Max<2.5', 'Avg>2.5', 'Avg<2.5'
            ]
            row = {col: '0' for col in columns}
            reverse_club_map = {v: k for k, v in url.club_to_odds_api.items()}
            row.update({
                'HomeTeam': reverse_club_map.get(home_team, home_team),
                'AwayTeam': reverse_club_map.get(away_team, away_team),
                'Day_of_week': week_day,
                'Day': day,
                'Month': month,
                'Year': year
            })
            for key in ['B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA', 'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA']:
                if key in odds_1x2:
                    row[key] = str(odds_1x2[key])
            for key in ['B365>2.5', 'B365<2.5', 'Max>2.5', 'Max<2.5', 'Avg>2.5', 'Avg<2.5']:
                if key in odds_goals:
                    row[key] = str(odds_goals[key])
            df = pd.DataFrame([row], columns=columns)
            df.to_csv('NextGame.csv', index=False)
            logger.info("Successfully saved match data to NextGame.csv with columns: %s", columns)
        except Exception as e:
            logger.error(f"Error saving CSV: {str(e)}")

    def get_next_game_data(self, odds_url: str, star_club: str, opp_club: str, game_date: str, league: str = "Serie A") -> Dict[str, str]:
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
        event = self.find_match(events, star_club, opp_club, league, game_date)
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
        event = self.find_match(events, star_club, opp_club, league, game_date)
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

    def get_full_teams(self) -> Dict[str, Dict[str, List[str]]]:
        """Retrieve all club names from The Odds API and compare with url.clubs_by_league."""
        result = {
            "odds_api_teams": {},
            "local_teams": {},
            "matches": {},
            "mismatches": {}
        }
        for league in url.available_leagues:
            logger.info(f"Fetching teams for {league}")
            result["local_teams"][league] = sorted(url.clubs_by_league.get(league, []))
            events = self.fetch_odds(league)
            odds_api_teams = set()
            if events:
                for event in events:
                    if event.get('home_team'):
                        odds_api_teams.add(event.get('home_team'))
                    if event.get('away_team'):
                        odds_api_teams.add(event.get('away_team'))
            result["odds_api_teams"][league] = sorted(list(odds_api_teams))
            api_teams_lower = {team.lower() for team in odds_api_teams}
            matches = []
            for local_team in result["local_teams"][league]:
                api_team = url.club_to_odds_api.get(local_team, local_team).lower()
                if api_team in api_teams_lower:
                    matches.append(local_team)
            mismatches = [team for team in result["local_teams"][league] if team not in matches]
            result["matches"][league] = sorted(matches)
            result["mismatches"][league] = sorted(mismatches)
            print(f"\n{league}:")
            print("  Odds API Teams:")
            for i, team in enumerate(result["odds_api_teams"][league], 1):
                print(f"    {i}. {team}")
            print("  Local Teams (url.clubs_by_league):")
            for i, team in enumerate(result["local_teams"][league], 1):
                print(f"    {i}. {team}")
            print("  Matching Teams:")
            for i, team in enumerate(result["matches"][league], 1):
                print(f"    {i}. {team}")
            print("  Mismatched Teams:")
            for i, team in enumerate(result["mismatches"][league], 1):
                print(f"    {i}. {team}")
            logger.info(f"{league} - Odds API teams: {len(odds_api_teams)}, Local teams: {len(result['local_teams'][league])}, Matches: {len(matches)}, Mismatches: {len(mismatches)}")
        return result

# Singleton instance
_SCRAPER_INSTANCE = None

def get_scraper(api_key: str = "6521a8f852098babe8777208742ae518"):
    global _SCRAPER_INSTANCE
    if _SCRAPER_INSTANCE is None:
        _SCRAPER_INSTANCE = NextGameScraper(api_key)
    return _SCRAPER_INSTANCE

def get_next_game_data(odds_url: str, star_club: str = None, opp_club: str = None, game_date: str = None, league: str = "Serie A") -> Dict[str, str]:
    if star_club is None or opp_club is None or game_date is None or league is None:
        logger.warning(f"Missing parameters: star_club={star_club}, opp_club={opp_club}, game_date={game_date}, league={league}")
        if game_date is None:
            game_date = datetime.now().strftime("%d/%m/%Y")
    scraper = get_scraper()
    return scraper.get_next_game_data(odds_url, star_club, opp_club, game_date, league)

def get_next_game_goals_data(odds_url: str, star_club: str = None, opp_club: str = None, game_date: str = None, league: str = "Serie A") -> Dict[str, str]:
    if star_club is None or opp_club is None or game_date is None or league is None:
        logger.warning(f"Missing parameters: star_club={star_club}, opp_club={opp_club}, game_date={game_date}, league={league}")
        if game_date is None:
            game_date = datetime.now().strftime("%d/%m/%Y")
    scraper = get_scraper()
    return scraper.get_next_game_goals_data(odds_url, star_club, opp_club, game_date, league)