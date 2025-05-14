
import pandas as pd
import requests
import json
import logging
from datetime import datetime, timezone
import os
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def get_next_game_data(odds_url: str, star_club: str, opp_club: str, game_date: str, league: str, allow_prompt: bool = True) -> dict:
    """
    Fetch 1X2 odds for the next game using The Odds API.
    If no match is found, returns an error with a list of upcoming games.
    Prompts for game selection only if allow_prompt is True and running on macOS.
    """
    logger.info(f"Getting odds for {star_club} vs {opp_club} in {league}")
    
    try:
        # Parse game date
        game_datetime = datetime.strptime(game_date, "%d/%m/%Y")
        game_datetime = game_datetime.replace(tzinfo=timezone.utc)
        
        # Map league to Odds API sport key
        league_map = {
            "Premier League": "soccer_epl",
            "Bundesliga": "soccer_germany_bundesliga",
            "La Liga": "soccer_spain_la_liga",
            "Serie A": "soccer_italy_serie_a",
            "Primeira Liga": "soccer_portugal_primeira_liga",
            "Ligue 1": "soccer_france_ligue_one"
        }
        sport_key = league_map.get(league)
        if not sport_key:
            return {"error": f"League {league} not supported by The Odds API"}
        
        logger.info(f"Fetching odds for {league} ({sport_key})")
        api_key = '6521a8f852098babe8777208742ae518'
        if not api_key:
            raise ValueError("ODDS_API_KEY environment variable not set")
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions=eu&markets=h2h,totals&oddsFormat=decimal"
        
        response = requests.get(url)
        response.raise_for_status()
        events = response.json()
        logger.info(f"Fetched {len(events)} events from The Odds API")
        
        # Log available bookmakers
        bookmakers = set()
        for event in events:
            for bookmaker in event.get("bookmakers", []):
                bookmakers.add(bookmaker["key"])
        logger.info(f"Available bookmakers: {', '.join(bookmakers)}")
        
        # Search for the match
        logger.info(f"Searching for match: {star_club} vs {opp_club} in {league}")
        logger.info(f"Filtering for game date: {game_datetime.strftime('%Y-%m-%d')}")
        
        # Normalize team names
        def normalize_team_name(name: str) -> str:
            import unicodedata
            name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
            return name.lower().replace(" ", "")
        
        star_club_norm = normalize_team_name(star_club)
        opp_club_norm = normalize_team_name(opp_club)
        
        matching_events = []
        upcoming_games = []
        for event in events:
            commence_time = datetime.fromisoformat(event["commence_time"].replace("Z", "+00:00"))
            home_team_norm = normalize_team_name(event["home_team"])
            away_team_norm = normalize_team_name(event["away_team"])
            
            # Collect upcoming games within 7 days
            if (commence_time - game_datetime).total_seconds() <= 7 * 86400:
                upcoming_games.append({
                    "game": f"{event['home_team']} vs {event['away_team']}",
                    "date": commence_time.strftime("%Y-%m-%d %H:%M UTC"),
                    "event": event
                })
            
            # Check for exact match
            if (home_team_norm == star_club_norm and away_team_norm == opp_club_norm) or \
               (home_team_norm == opp_club_norm and away_team_norm == star_club_norm):
                if abs((commence_time - game_datetime).total_seconds()) <= 86400:  # 1 day
                    matching_events.append(event)
        
        logger.info(f"Found {len(matching_events)} matching events")
        
        if not matching_events:
            logger.warning(f"No match found for {star_club} vs {opp_club}. Returning upcoming games list.")
            upcoming_games_list = [
                f"  {i+1}. {game['game']} at {game['date']}"
                for i, game in enumerate(upcoming_games)
            ]
            return {
                "error": f"No match found for {star_club} vs {opp_club} in {league} on {game_date}.",
                "upcoming_games": upcoming_games_list,
                "events": [game["event"] for game in upcoming_games]
            }
        
        # Process the first matching event
        event = matching_events[0]
        bookmakers = event.get("bookmakers", [])
        logger.info(f"Bookmakers with odds: {', '.join([b['key'] for b in bookmakers])}")
        
        odds_data = {
            "HomeTeam": star_club,
            "AwayTeam": opp_club,
            "Day": game_datetime.day,
            "Month": game_datetime.month,
            "Year": game_datetime.year,
            "Day_of_week": game_datetime.strftime("%A")
        }
        
        # Collect 1X2 odds
        bookmaker_map = {
            "bet365": ["B365H", "B365D", "B365A"],
            "bwin": ["BWH", "BWD", "BWA"],
            "betclic": ["BTCH", "BTCD", "BTCA"],
            "winamax_de": ["WDH", "WDD", "WDA"],
            "winamax_fr": ["WMH", "WMD", "WMA"],
            "tipico_de": ["TIH", "TID", "TIA"],
            "betfair_ex_eu": ["BFH", "BFD", "BFA"],
            "nordicbet": ["NBH", "NBD", "NBA"],
            "betsson": ["BSH", "BSD", "BSA"]
        }
        
        h2h_bookmakers = []
        for bookmaker in bookmakers:
            for market in bookmaker.get("markets", []):
                if market["key"] == "h2h":
                    h2h_bookmakers.append(bookmaker["key"])
                    outcomes = {o["name"]: o["price"] for o in market["outcomes"]}
                    if bookmaker["key"] in bookmaker_map:
                        keys = bookmaker_map[bookmaker["key"]]
                        odds_data[keys[0]] = outcomes.get(star_club, outcomes.get(event["home_team"]))
                        odds_data[keys[1]] = outcomes.get("Draw")
                        odds_data[keys[2]] = outcomes.get(opp_club, outcomes.get(event["away_team"]))
        
        logger.info(f"Bookmakers with 1X2 odds: {', '.join(h2h_bookmakers)}")
        
        # Calculate Max and Avg odds
        h_odds = [odds_data.get(key) for key in odds_data if key.endswith("H") and odds_data.get(key)]
        d_odds = [odds_data.get(key) for key in odds_data if key.endswith("D") and odds_data.get(key)]
        a_odds = [odds_data.get(key) for key in odds_data if key.endswith("A") and odds_data.get(key)]
        
        if h_odds:
            odds_data["MaxH"] = max(h_odds)
            odds_data["AvgH"] = sum(h_odds) / len(h_odds)
        if d_odds:
            odds_data["MaxD"] = max(d_odds)
            odds_data["AvgD"] = sum(d_odds) / len(d_odds)
        if a_odds:
            odds_data["MaxA"] = max(a_odds)
            odds_data["AvgA"] = sum(a_odds) / len(a_odds)
        
        # Substitute missing bet365 or bwin odds
        if "B365H" not in odds_data and h2h_bookmakers:
            substitute = "pinnacle" if "pinnacle" in h2h_bookmakers else h2h_bookmakers[0]
            logger.info(f"Using {substitute} as substitute for bet365 (1X2 odds)")
            for market in next(b for b in bookmakers if b["key"] == substitute).get("markets", []):
                if market["key"] == "h2h":
                    outcomes = {o["name"]: o["price"] for o in market["outcomes"]}
                    odds_data["B365H"] = outcomes.get(star_club, outcomes.get(event["home_team"]))
                    odds_data["B365D"] = outcomes.get("Draw")
                    odds_data["B365A"] = outcomes.get(opp_club, outcomes.get(event["away_team"]))
        
        if "BWH" not in odds_data and h2h_bookmakers:
            substitute = "unibet_eu" if "unibet_eu" in h2h_bookmakers else h2h_bookmakers[0]
            logger.info(f"Using {substitute} as substitute for bwin (1X2 odds)")
            for market in next(b for b in bookmakers if b["key"] == substitute).get("markets", []):
                if market["key"] == "h2h":
                    outcomes = {o["name"]: o["price"] for o in market["outcomes"]}
                    odds_data["BWH"] = outcomes.get(star_club, outcomes.get(event["home_team"]))
                    odds_data["BWD"] = outcomes.get("Draw")
                    odds_data["BWA"] = outcomes.get(opp_club, outcomes.get(event["away_team"]))
        
        # Save to NextGame.csv
        df = pd.DataFrame([odds_data])
        df.to_csv("NextGame.csv", index=False)
        logger.info(f"Successfully saved match data to NextGame.csv with columns: {list(df.columns)}")
        
        return odds_data
    
    except Exception as e:
        logger.error(f"Error fetching 1X2 odds: {str(e)}")
        return {"error": str(e)}

def get_next_game_goals_data(odds_url: str, star_club: str, opp_club: str, game_date: str, league: str, allow_prompt: bool = True) -> dict:
    """
    Fetch over/under 2.5 goals odds for the next game using The Odds API.
    If no match is found, returns an error with a list of upcoming games.
    Prompts for game selection only if allow_prompt is True and running on macOS.
    """
    logger.info(f"Getting goals odds for {star_club} vs {opp_club} in {league}")
    
    try:
        game_datetime = datetime.strptime(game_date, "%d/%m/%Y")
        game_datetime = game_datetime.replace(tzinfo=timezone.utc)
        
        league_map = {
            "Premier League": "soccer_epl",
            "Bundesliga": "soccer_germany_bundesliga",
            "La Liga": "soccer_spain_la_liga",
            "Serie A": "soccer_italy_serie_a",
            "Primeira Liga": "soccer_portugal_primeira_liga",
            "Ligue 1": "soccer_france_ligue_one"
        }
        sport_key = league_map.get(league)
        if not sport_key:
            return {"error": f"League {league} not supported by The Odds API"}
        
        logger.info(f"Fetching odds for {league} ({sport_key})")
        api_key = os.getenv("ODDS_API_KEY")
        if not api_key:
            raise ValueError("ODDS_API_KEY environment variable not set")
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions=eu&markets=totals&oddsFormat=decimal"
        
        response = requests.get(url)
        response.raise_for_status()
        events = response.json()
        logger.info(f"Fetched {len(events)} events from The Odds API")
        
        def normalize_team_name(name: str) -> str:
            import unicodedata
            name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
            return name.lower().replace(" ", "")
        
        star_club_norm = normalize_team_name(star_club)
        opp_club_norm = normalize_team_name(opp_club)
        
        matching_events = []
        upcoming_games = []
        for event in events:
            commence_time = datetime.fromisoformat(event["commence_time"].replace("Z", "+00:00"))
            home_team_norm = normalize_team_name(event["home_team"])
            away_team_norm = normalize_team_name(event["away_team"])
            
            if (commence_time - game_datetime).total_seconds() <= 7 * 86400:
                upcoming_games.append({
                    "game": f"{event['home_team']} vs {event['away_team']}",
                    "date": commence_time.strftime("%Y-%m-%d %H:%M UTC"),
                    "event": event
                })
            
            if (home_team_norm == star_club_norm and away_team_norm == opp_club_norm) or \
               (home_team_norm == opp_club_norm and away_team_norm == star_club_norm):
                if abs((commence_time - game_datetime).total_seconds()) <= 86400:
                    matching_events.append(event)
        
        logger.info(f"Found {len(matching_events)} matching events")
        
        if not matching_events:
            logger.warning(f"No match found for {star_club} vs {opp_club}. Returning upcoming games list.")
            upcoming_games_list = [
                f"  {i+1}. {game['game']} at {game['date']}"
                for i, game in enumerate(upcoming_games)
            ]
            return {
                "error": f"No match found for {star_club} vs {opp_club} in {league} on {game_date}.",
                "upcoming_games": upcoming_games_list,
                "events": [game["event"] for game in upcoming_games]
            }
        
        event = matching_events[0]
        bookmakers = event.get("bookmakers", [])
        logger.info(f"Bookmakers with odds: {', '.join([b['key'] for b in bookmakers])}")
        
        goals_odds = {}
        totals_bookmakers = []
        for bookmaker in bookmakers:
            for market in bookmaker.get("markets", []):
                if market["key"] == "totals" and market.get("outcomes"):
                    totals_bookmakers.append(bookmaker["key"])
                    for outcome in market["outcomes"]:
                        if outcome["point"] == 2.5:
                            key = f"{bookmaker['key']}>{outcome['name'].lower()}" if outcome["name"] == "Over" else f"{bookmaker['key']}<{outcome['name'].lower()}"
                            goals_odds[key] = outcome["price"]
        
        logger.info(f"Bookmakers with totals (2.5) odds: {', '.join(totals_bookmakers)}")
        logger.info(f"Collected goals odds from {len(totals_bookmakers)} bookmakers")
        
        if not totals_bookmakers:
            logger.warning("No totals odds found. Returning default odds.")
            return {
                "B365>2.5": 0,
                "B365<2.5": 0,
                "Max>2.5": 0,
                "Max<2.5": 0,
                "Avg>2.5": 0,
                "Avg<2.5": 0
            }
        
        # Calculate Max and Avg for goals odds
        over_odds = [v for k, v in goals_odds.items() if k.endswith(">over") and v]
        under_odds = [v for k, v in goals_odds.items() if k.endswith(">under") and v]
        
        if over_odds:
            goals_odds["Max>2.5"] = max(over_odds)
            goals_odds["Avg>2.5"] = sum(over_odds) / len(over_odds)
        if under_odds:
            goals_odds["Max<2.5"] = max(under_odds)
            goals_odds["Avg<2.5"] = sum(under_odds) / len(under_odds)
        
        # Ensure bet365 keys
        if "bet365>over" in goals_odds:
            goals_odds["B365>2.5"] = goals_odds["bet365>over"]
            goals_odds["B365<2.5"] = goals_odds["bet365>under"]
        else:
            substitute = "pinnacle" if "pinnacle>over" in goals_odds else next(iter(totals_bookmakers), None)
            if substitute:
                logger.info(f"Using {substitute} as substitute for bet365 (totals odds)")
                goals_odds["B365>2.5"] = goals_odds.get(f"{substitute}>over", 0)
                goals_odds["B365<2.5"] = goals_odds.get(f"{substitute}>under", 0)
            else:
                goals_odds["B365>2.5"] = 0
                goals_odds["B365<2.5"] = 0
        
        return goals_odds
    
    except Exception as e:
        logger.error(f"Error fetching goals odds: {str(e)}")
        return {"error": str(e)}
