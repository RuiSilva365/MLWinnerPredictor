
# api_handler.py
import json
import pandas as pd
import os
from typing import Dict, Optional, Tuple, List, Any
import treatment
import nextGameScrapping
import prediction
import uuid
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

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

@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """
    Endpoint to check the status of a data processing job
    """
    if job_id not in jobs:
        return jsonify({'status': 'error', 'message': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    response = {
        'status': job['status'],
        'job_id': job_id
    }
    
    if job['status'] == 'completed':
        response['result'] = job['result']
    elif job['status'] == 'error':
        response['error'] = job['error']
    
    return jsonify(response)

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
        odds_data = nextGameScrapping.get_next_game_data(
            odds_url=odds_url, 
            star_club=star_club, 
            opp_club=opp_club, 
            game_date=game_date, 
            league=league,
            allow_prompt=False,
            selected_event=selected_event
        )
        
        if 'error' in odds_data and not selected_event:
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
        
        goals_data = nextGameScrapping.get_next_game_goals_data(
            odds_url=odds_url, 
            star_club=star_club, 
            opp_club=opp_club, 
            game_date=game_date, 
            league=league,
            allow_prompt=False,
            selected_event=selected_event
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
                'odds': odds_data,
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
