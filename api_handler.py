import json
import pandas as pd
import os
from typing import Dict, Optional, Tuple, List, Any
import treatment
import nextGame
import prediction
import uuid
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# In-memory storage for job status
jobs = {}

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """
    Endpoint to check the status of a job
    """
    if job_id not in jobs:
        return jsonify({
            'status': 'error',
            'message': f'Job ID {job_id} not found'
        }), 404
    
    return jsonify(jobs[job_id])

@app.route('/api/predict', methods=['POST'])
def predict_game():
    """
    Endpoint to start a game data processing job
    """
    data = request.json
    
    required_fields = ['season', 'league', 'team1', 'team2', 'gameDate']
    if not all(field in data for field in required_fields):
        return jsonify({
            'status': 'error', 
            'message': f'Missing required fields: {", ".join(required_fields)}'
        }), 400
    
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        'status': 'pending',
        'params': data,
        'result': None,
        'error': None
    }
    
    try:
        process_game_data(job_id, data)
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)
    
    return jsonify({
        'status': 'accepted',
        'job_id': job_id,
        'message': 'Data processing job started'
    })

@app.route('/api/data/team', methods=['GET'])
def get_team_data():
    """
    Endpoint to get processed data for a specific team
    """
    team_param = request.args.get('team')
    
    if not team_param:
        return jsonify({'status': 'error', 'message': 'Team parameter is required'}), 400
    
    try:
        file_path = "TeamGamesTreated.csv" if team_param == "team1" else "OppGamesTreated.csv"
        
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': f'Data file {file_path} not found'}), 404
        
        df = pd.read_csv(file_path)
        
        result = {
            'status': 'success',
            'data': df.to_dict(orient='records'),
            'shape': df.shape,
            'columns': df.columns.tolist()
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error retrieving team data: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/data/next-game', methods=['GET'])
def get_next_game():
    """
    Endpoint to get next game data
    """
    try:
        file_path = "NextGame.csv"
        
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': 'Next game data not found'}), 404
        
        df = pd.read_csv(file_path)
        
        result = {
            'status': 'success',
            'data': df.to_dict(orient='records'),
            'shape': df.shape,
            'columns': df.columns.tolist()
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error retrieving next game data: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/leagues', methods=['GET'])
def get_leagues():
    """
    Endpoint to get available leagues
    """
    import url
    
    leagues = list(url.clubs_by_league.keys())
    return jsonify({
        'status': 'success',
        'leagues': leagues
    })

@app.route('/api/teams', methods=['GET'])
def get_teams():
    """
    Endpoint to get teams for a specific league
    """
    import url
    
    league = request.args.get('league')
    
    if not league:
        return jsonify({'status': 'error', 'message': 'League parameter is required'}), 400
    
    logger.info(f"Get teams request: league={league!r}")
    
    if league not in url.clubs_by_league:
        return jsonify({'status': 'error', 'message': f'League {league} not found'}), 404
    
    teams = url.clubs_by_league[league]
    return jsonify({
        'status': 'success',
        'league': league,
        'teams': teams
    })

def process_game_data(job_id: str, data: Dict[str, Any]) -> None:
    """
    Process game data (create and save dataframes) and update job status
    """
    try:
        season = int(data['season'])
        league = data['league']
        star_club = data['team1']
        opp_club = data['team2']
        game_date = data['gameDate']
        selected_event = data.get('selected_event')  # Get selected event if available
        
        # If we have a selected event, map team names first
        if selected_event:
            # Import the team name mapping if not already imported
            from team_name_mapping import normalize_team_name, get_standard_team_name, TEAM_MAPPINGS
            
            # Get the normalized team names from the API
            api_home_team = selected_event["home_team"]
            api_away_team = selected_event["away_team"]
            
            # Check if API team names match our standardized names
            home_normalized = normalize_team_name(api_home_team)
            away_normalized = normalize_team_name(api_away_team)
            
            # Log the normalization process
            logger.info(f"Normalizing team names:")
            logger.info(f"  API Home: '{api_home_team}' → normalized: '{home_normalized}'")
            logger.info(f"  API Away: '{api_away_team}' → normalized: '{away_normalized}'")
            
            # Special case handling for common API naming differences
            special_cases = {
                'sportinglisbon': 'Sp Lisbon',
                'vitóriasc': 'guimaraes',
                'vitoriasc': 'guimaraes'
            }
            
            # Apply special case mapping if needed
            if home_normalized in special_cases:
                star_club = special_cases[home_normalized]
                logger.info(f"  Applied special mapping for home team: {api_home_team} → {star_club}")
            else:
                star_club = get_standard_team_name(api_home_team)
                logger.info(f"  Mapped home team: {api_home_team} → {star_club}")
            
            if away_normalized in special_cases:
                opp_club = special_cases[away_normalized]
                logger.info(f"  Applied special mapping for away team: {api_away_team} → {opp_club}")
            else:
                opp_club = get_standard_team_name(api_away_team)
                logger.info(f"  Mapped away team: {api_away_team} → {opp_club}")
            
            # Update the data dictionary with the standardized names
            data['team1'] = star_club
            data['team2'] = opp_club
            
            logger.info(f"Using standardized team names for processing: {star_club} vs {opp_club}")
        
        league_url_segment = league.lower().replace(' ', '-')
        team1_url = star_club.lower().replace(' ', '-')
        team2_url = opp_club.lower().replace(' ', '-')
        odds_url = f"https://www.oddsportal.com/football/{league_url_segment}/{team1_url}-{team2_url}"
        
        jobs[job_id]['status'] = 'processing'
        
        logger.info(f"Processing historical data for {star_club} vs {opp_club} in {league}...")
        error = treatment.handler(season, league, star_club, opp_club)
        if error:
            logger.error(f"treatment.handler failed: {error}")
            jobs[job_id]['status'] = 'error'
            jobs[job_id]['error'] = error
            return
        
        team_games = pd.read_csv("TeamGames.csv")
        opp_games = pd.read_csv("OppGames.csv")
        
        logger.info("Adding TotalGoals column...")
        team_games = treatment.add_total_goals_column(team_games)
        opp_games = treatment.add_total_goals_column(opp_games)
        
        logger.info("Adding FTR odds feedback columns...")
        team_games = treatment.add_FTRodds_feedback(team_games)
        opp_games = treatment.add_FTRodds_feedback(opp_games)
        
        logger.info("Adding goals odds feedback columns...")
        team_games = treatment.add_Goalsodds_feedback(team_games)
        opp_games = treatment.add_Goalsodds_feedback(opp_games)
        
        logger.info("Processing dates...")
        team_games = treatment.treatment_of_date(team_games)
        opp_games = treatment.treatment_of_date(opp_games)
        
        logger.info("Dropping Date column if it exists...")
        if 'Date' in team_games.columns:
            team_games = team_games.drop('Date', axis=1)
        if 'Date' in opp_games.columns:
            opp_games = opp_games.drop('Date', axis=1)
        
        logger.info("Dropping WeekDay column if it exists...")
        if 'WeekDay' in team_games.columns:
            team_games = team_games.drop('WeekDay', axis=1)
        if 'WeekDay' in opp_games.columns:
            opp_games = opp_games.drop('WeekDay', axis=1)
        
        logger.info("Saving treated files: TeamGamesTreated.csv, OppGamesTreated.csv")
        team_games.to_csv("TeamGamesTreated.csv", index=False)
        opp_games.to_csv("OppGamesTreated.csv", index=False)
        
        logger.info(f"Fetching odds for upcoming game: {odds_url}")
        
        # If we have a selected event, process it directly
        if selected_event:
            logger.info(f"Using selected event: {selected_event['home_team']} vs {selected_event['away_team']}")
            
            # Parse commence_time from selected_event
            commence_time = datetime.datetime.fromisoformat(selected_event["commence_time"].replace("Z", "+00:00"))
                    
            # Create odds data dictionary
            odds_data = {
                "HomeTeam": star_club,  # Already mapped
                "AwayTeam": opp_club,   # Already mapped
                "Day": commence_time.day,
                "Month": commence_time.month,
                "Year": commence_time.year,
                "Day_of_week": commence_time.strftime("%A")
            }
            
            # Process bookmakers
            bookmakers = selected_event.get("bookmakers", [])
            
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
                        
                        # Map the bookmaker outcomes to our standardized team names
                        team_outcomes = {}
                        for outcome_name, price in outcomes.items():
                            if outcome_name == api_home_team:
                                team_outcomes[star_club] = price
                            elif outcome_name == api_away_team:
                                team_outcomes[opp_club] = price
                            else:
                                team_outcomes[outcome_name] = price
                        
                        if bookmaker["key"] in bookmaker_map:
                            keys = bookmaker_map[bookmaker["key"]]
                            odds_data[keys[0]] = team_outcomes.get(star_club, 0)
                            odds_data[keys[1]] = team_outcomes.get("Draw", 0)
                            odds_data[keys[2]] = team_outcomes.get(opp_club, 0)
            
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
                        # Map API team names to our standardized names
                        team_outcomes = {}
                        for outcome_name, price in outcomes.items():
                            if outcome_name == api_home_team:
                                team_outcomes[star_club] = price
                            elif outcome_name == api_away_team:
                                team_outcomes[opp_club] = price
                            else:
                                team_outcomes[outcome_name] = price
                                
                        odds_data["B365H"] = team_outcomes.get(star_club, 0)
                        odds_data["B365D"] = team_outcomes.get("Draw", 0)
                        odds_data["B365A"] = team_outcomes.get(opp_club, 0)
            
            if "BWH" not in odds_data and h2h_bookmakers:
                substitute = "unibet_eu" if "unibet_eu" in h2h_bookmakers else h2h_bookmakers[0]
                logger.info(f"Using {substitute} as substitute for bwin (1X2 odds)")
                for market in next(b for b in bookmakers if b["key"] == substitute).get("markets", []):
                    if market["key"] == "h2h":
                        outcomes = {o["name"]: o["price"] for o in market["outcomes"]}
                        # Map API team names to our standardized names
                        team_outcomes = {}
                        for outcome_name, price in outcomes.items():
                            if outcome_name == api_home_team:
                                team_outcomes[star_club] = price
                            elif outcome_name == api_away_team:
                                team_outcomes[opp_club] = price
                            else:
                                team_outcomes[outcome_name] = price
                                
                        odds_data["BWH"] = team_outcomes.get(star_club, 0)
                        odds_data["BWD"] = team_outcomes.get("Draw", 0)
                        odds_data["BWA"] = team_outcomes.get(opp_club, 0)
            
            # Save to NextGame.csv
            df = pd.DataFrame([odds_data])
            df.to_csv("NextGame.csv", index=False)
            logger.info(f"Successfully saved match data to NextGame.csv with columns: {list(df.columns)}")
            
            # Process goals odds for the same event
            goals_data = {}
            totals_bookmakers = []
            
            for bookmaker in bookmakers:
                for market in bookmaker.get("markets", []):
                    if market["key"] == "totals" and market.get("outcomes"):
                        for outcome in market["outcomes"]:
                            if outcome["point"] == 2.5:
                                totals_bookmakers.append(bookmaker["key"])
                                key = f"{bookmaker['key']}>{outcome['name'].lower()}" if outcome["name"] == "Over" else f"{bookmaker['key']}<{outcome['name'].lower()}"
                                goals_data[key] = outcome["price"]
            
            logger.info(f"Bookmakers with totals (2.5) odds: {', '.join(set(totals_bookmakers))}")
            
            # Calculate Max and Avg for goals odds
            over_odds = [v for k, v in goals_data.items() if "over" in k.lower() and v]
            under_odds = [v for k, v in goals_data.items() if "under" in k.lower() and v]
            
            if over_odds:
                goals_data["Max>2.5"] = max(over_odds)
                goals_data["Avg>2.5"] = sum(over_odds) / len(over_odds)
            else:
                goals_data["Max>2.5"] = 0
                goals_data["Avg>2.5"] = 0
                
            if under_odds:
                goals_data["Max<2.5"] = max(under_odds)
                goals_data["Avg<2.5"] = sum(under_odds) / len(under_odds)
            else:
                goals_data["Max<2.5"] = 0
                goals_data["Avg<2.5"] = 0
            
            # Ensure bet365 keys
            if "bet365>over" in goals_data:
                goals_data["B365>2.5"] = goals_data["bet365>over"]
                goals_data["B365<2.5"] = goals_data["bet365<under"]
            else:
                substitute = "pinnacle" if "pinnacle>over" in goals_data else next(iter(totals_bookmakers), None)
                if substitute:
                    logger.info(f"Using {substitute} as substitute for bet365 (totals odds)")
                    goals_data["B365>2.5"] = goals_data.get(f"{substitute}>over", 0)
                    goals_data["B365<2.5"] = goals_data.get(f"{substitute}<under", 0)
                else:
                    goals_data["B365>2.5"] = 0
                    goals_data["B365<2.5"] = 0
            
            # Update NextGame.csv with goals odds
            df = pd.read_csv("NextGame.csv")
            for key, value in goals_data.items():
                if key in ["B365>2.5", "B365<2.5", "Max>2.5", "Max<2.5", "Avg>2.5", "Avg<2.5"]:
                    df[key] = value
            df.to_csv("NextGame.csv", index=False)
            logger.info(f"Updated NextGame.csv with goals odds")
        else:
            # Try to get odds data normally - will return upcoming games if no match
            odds_data = nextGame.get_next_game_data(
                odds_url=odds_url, 
                star_club=star_club, 
                opp_club=opp_club, 
                game_date=game_date, 
                league=league,
                allow_prompt=False
            )
            
            if 'error' in odds_data:
                logger.warning(f"Failed to fetch odds: {odds_data['error']}")
                result = {
                    'team1': {
                        'name': star_club,
                        'games_count': len(team_games),
                        'columns': team_games.columns.tolist()
                    },
                    'team2': {
                        'name': opp_club,
                        'games_count': len(opp_games),
                        'columns': opp_games.columns.tolist()
                    },
                    'next_game': {
                        'odds_error': odds_data['error'],
                        'upcoming_games': odds_data.get('upcoming_games', []),
                        'events': odds_data.get('events', [])
                    }
                }
                jobs[job_id]['status'] = 'pending_game_selection'
                jobs[job_id]['result'] = result
                return
            
            # If we get here, odds data was found successfully
            goals_data = nextGame.get_next_game_goals_data(
                odds_url=odds_url, 
                star_club=star_club, 
                opp_club=opp_club, 
                game_date=game_date, 
                league=league,
                allow_prompt=False
            )
            
            if 'error' in goals_data:
                logger.warning(f"Failed to fetch goals odds: {goals_data['error']}. Using default odds.")
                goals_data = {
                    "B365>2.5": 0,
                    "B365<2.5": 0,
                    "Max>2.5": 0,
                    "Max<2.5": 0,
                    "Avg>2.5": 0,
                    "Avg<2.5": 0
                }
        
        # Run prediction
        logger.info("Running prediction...")
        next_game_df = pd.read_csv("NextGame.csv")
        prediction_result = prediction.predict(team_games, opp_games, next_game_df)
        
        result = {
            'team1': {
                'name': star_club,
                'games_count': len(team_games),
                'columns': team_games.columns.tolist()
            },
            'team2': {
                'name': opp_club,
                'games_count': len(opp_games),
                'columns': opp_games.columns.tolist()
            },
            'next_game': {
                'odds': odds_data if not selected_event else pd.read_csv("NextGame.csv").iloc[0].to_dict(),
                'goals_odds': goals_data,
                'prediction': prediction_result
            }
        }
        
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['result'] = result
        
    except Exception as e:
        logger.error(f"Error processing game data: {str(e)}")
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)