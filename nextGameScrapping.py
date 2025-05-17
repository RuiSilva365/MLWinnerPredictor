import pandas as pd
import requests
import json
import logging
from datetime import datetime, timezone, timedelta
import os
import unicodedata
from team_name_mapping import LEAGUE_API_MAPPING

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def get_next_game_data(odds_url: str, star_club: str, opp_club: str, game_date: str, league: str, allow_prompt: bool = True, selected_event=None) -> dict:
    """
    Fetch 1X2 odds for the next game using The Odds API.
    If no exact match is found, returns all league games for selection.
    If selected_event is provided, uses that instead of searching.
    """
    logger.info(f"Getting odds for {star_club} vs {opp_club} in {league}")
    
    try:
        # Parse game date
        game_datetime = datetime.strptime(game_date, "%d/%m/%Y")
        game_datetime = game_datetime.replace(tzinfo=timezone.utc)
        
        # If a specific event was selected, use it directly
        if selected_event:
            logger.info(f"Using selected event: {selected_event['home_team']} vs {selected_event['away_team']}")
            return process_event(selected_event, star_club, opp_club, game_datetime)
        
        # Map league to Odds API sport key
        sport_key = LEAGUE_API_MAPPING.get(league)
        if not sport_key:
            return {"error": f"League {league} not supported by The Odds API"}
        
        logger.info(f"Fetching odds for {league} ({sport_key})")
        api_key = os.getenv("ODDS_API_KEY", "6521a8f852098babe8777208742ae518")
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions=eu&markets=h2h,totals&oddsFormat=decimal"
        
        response = requests.get(url)
        response.raise_for_status()
        events = response.json()
        logger.info(f"Fetched {len(events)} events from The Odds API")
        
        # Log available bookmakers for debugging
        bookmakers = set()
        for event in events:
            for bookmaker in event.get("bookmakers", []):
                bookmakers.add(bookmaker["key"])
        logger.info(f"Available bookmakers: {', '.join(bookmakers)}")
        
        # Log all events for debugging
        logger.info("Available events:")
        for i, event in enumerate(events):
            logger.info(f"  {i+1}. {event['home_team']} vs {event['away_team']} - {event['commence_time']}")
        
        # Always collect upcoming games
        upcoming_games = []
        for event in events:
            commence_time = datetime.fromisoformat(event["commence_time"].replace("Z", "+00:00"))
            date_diff = abs((commence_time - game_datetime).total_seconds()) / 86400
            
            # Include games within 7 days of target date
            if date_diff <= 7:
                upcoming_games.append({
                    "game": f"{event['home_team']} vs {event['away_team']}",
                    "date": commence_time.strftime("%Y-%m-%d %H:%M UTC"),
                    "event": event
                })
        
        logger.info(f"Found {len(upcoming_games)} upcoming games in {league}")
        
        # Return upcoming games for selection
        if upcoming_games:
            upcoming_games_list = [
                f"  {i+1}. {game['game']} at {game['date']}"
                for i, game in enumerate(upcoming_games)
            ]
            return {
                "error": f"Please select a match for {star_club} vs {opp_club} in {league}.",
                "upcoming_games": upcoming_games_list,
                "events": [game["event"] for game in upcoming_games]
            }
        else:
            logger.warning(f"No upcoming games found for {league}")
            return {"error": f"No upcoming games found for {league}"}
        
    except Exception as e:
        logger.error(f"Error fetching 1X2 odds: {str(e)}")
        return {"error": str(e)}

def process_event(event, star_club, opp_club, game_datetime):
    """Process a selected event to extract odds data"""
    home_team = event["home_team"]
    away_team = event["away_team"]
    bookmakers = event.get("bookmakers", [])
    logger.info(f"Processing odds for {home_team} vs {away_team}")
    
    # Create odds data dictionary for the CSV
    odds_data = {
        "HomeTeam": home_team,
        "AwayTeam": away_team,
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
                    odds_data[keys[0]] = outcomes.get(home_team, 0)
                    odds_data[keys[1]] = outcomes.get("Draw", 0)
                    odds_data[keys[2]] = outcomes.get(away_team, 0)
    
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
    
    # Substitute missing bet365 or bwin odds if needed
    if "B365H" not in odds_data and h2h_bookmakers:
        substitute = "pinnacle" if "pinnacle" in h2h_bookmakers else h2h_bookmakers[0]
        logger.info(f"Using {substitute} as substitute for bet365 (1X2 odds)")
        for market in next(b for b in bookmakers if b["key"] == substitute).get("markets", []):
            if market["key"] == "h2h":
                outcomes = {o["name"]: o["price"] for o in market["outcomes"]}
                odds_data["B365H"] = outcomes.get(home_team, 0)
                odds_data["B365D"] = outcomes.get("Draw", 0)
                odds_data["B365A"] = outcomes.get(away_team, 0)
    
    if "BWH" not in odds_data and h2h_bookmakers:
        substitute = "unibet_eu" if "unibet_eu" in h2h_bookmakers else h2h_bookmakers[0]
        logger.info(f"Using {substitute} as substitute for bwin (1X2 odds)")
        for market in next(b for b in bookmakers if b["key"] == substitute).get("markets", []):
            if market["key"] == "h2h":
                outcomes = {o["name"]: o["price"] for o in market["outcomes"]}
                odds_data["BWH"] = outcomes.get(home_team, 0)
                odds_data["BWD"] = outcomes.get("Draw", 0)
                odds_data["BWA"] = outcomes.get(away_team, 0)
    
    # Save to NextGame.csv
    df = pd.DataFrame([odds_data])
    df.to_csv("NextGame.csv", index=False)
    logger.info(f"Successfully saved match data to NextGame.csv with columns: {list(df.columns)}")
    
    return odds_data

def get_next_game_goals_data(odds_url: str, star_club: str, opp_club: str, game_date: str, league: str, allow_prompt: bool = True, selected_event=None) -> dict:
    """
    Fetch over/under 2.5 goals odds for the next game using The Odds API.
    If selected_event is provided, uses that instead of searching.
    """
    logger.info(f"Getting goals odds for {star_club} vs {opp_club} in {league}")
    
    try:
        # If a specific event was selected, use it directly
        if selected_event:
            logger.info(f"Using selected event for goals odds: {selected_event['home_team']} vs {selected_event['away_team']}")
            return process_goals_event(selected_event)
        
        # Parse game date
        game_datetime = datetime.strptime(game_date, "%d/%m/%Y")
        game_datetime = game_datetime.replace(tzinfo=timezone.utc)
        
        # Map league to Odds API sport key
        sport_key = LEAGUE_API_MAPPING.get(league)
        if not sport_key:
            return {"error": f"League {league} not supported by The Odds API"}
        
        logger.info(f"Fetching odds for {league} ({sport_key})")
        api_key = os.getenv("ODDS_API_KEY", "6521a8f852098babe8777208742ae518")
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions=eu&markets=totals&oddsFormat=decimal"
        
        response = requests.get(url)
        response.raise_for_status()
        events = response.json()
        logger.info(f"Fetched {len(events)} events from The Odds API for goals odds")
        
        # Return default odds since we always want the user to select the game first
        # and we'll use the selected game for both the 1X2 and goals odds
        return {
            "B365>2.5": 0,
            "B365<2.5": 0,
            "Max>2.5": 0,
            "Max<2.5": 0,
            "Avg>2.5": 0,
            "Avg<2.5": 0
        }
        
    except Exception as e:
        logger.error(f"Error fetching goals odds: {str(e)}")
        return {"error": str(e)}

def process_goals_event(event):
    """Process a selected event to extract goals odds data"""
    home_team = event["home_team"]
    away_team = event["away_team"]
    bookmakers = event.get("bookmakers", [])
    logger.info(f"Processing goals odds for {home_team} vs {away_team}")
    
    goals_odds = {}
    totals_bookmakers = []
    
    for bookmaker in bookmakers:
        for market in bookmaker.get("markets", []):
            if market["key"] == "totals" and market.get("outcomes"):
                for outcome in market["outcomes"]:
                    if outcome["point"] == 2.5:
                        totals_bookmakers.append(bookmaker["key"])
                        key = f"{bookmaker['key']}>{outcome['name'].lower()}" if outcome["name"] == "Over" else f"{bookmaker['key']}<{outcome['name'].lower()}"
                        goals_odds[key] = outcome["price"]
    
    logger.info(f"Bookmakers with totals (2.5) odds: {', '.join(set(totals_bookmakers))}")
    
    if not totals_bookmakers:
        logger.warning("No totals odds found. Using default values.")
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
    under_odds = [v for k, v in goals_odds.items() if k.endswith("<under") and v]
    
    if over_odds:
        goals_odds["Max>2.5"] = max(over_odds)
        goals_odds["Avg>2.5"] = sum(over_odds) / len(over_odds)
    else:
        goals_odds["Max>2.5"] = 0
        goals_odds["Avg>2.5"] = 0
        
    if under_odds:
        goals_odds["Max<2.5"] = max(under_odds)
        goals_odds["Avg<2.5"] = sum(under_odds) / len(under_odds)
    else:
        goals_odds["Max<2.5"] = 0
        goals_odds["Avg<2.5"] = 0
    
    # Ensure bet365 keys
    if "bet365>over" in goals_odds:
        goals_odds["B365>2.5"] = goals_odds["bet365>over"]
        goals_odds["B365<2.5"] = goals_odds["bet365<under"]
    else:
        substitute = "pinnacle" if "pinnacle>over" in goals_odds else next(iter(totals_bookmakers), None)
        if substitute:
            logger.info(f"Using {substitute} as substitute for bet365 (totals odds)")
            goals_odds["B365>2.5"] = goals_odds.get(f"{substitute}>over", 0)
            goals_odds["B365<2.5"] = goals_odds.get(f"{substitute}<under", 0)
        else:
            goals_odds["B365>2.5"] = 0
            goals_odds["B365<2.5"] = 0
    
    # Merge with existing NextGame.csv if it exists
    if os.path.exists("NextGame.csv"):
        df = pd.read_csv("NextGame.csv")
        for key, value in goals_odds.items():
            if key in ["B365>2.5", "B365<2.5", "Max>2.5", "Max<2.5", "Avg>2.5", "Avg<2.5"]:
                df[key] = value
        df.to_csv("NextGame.csv", index=False)
        logger.info(f"Updated NextGame.csv with goals odds")
    
    return goals_odds