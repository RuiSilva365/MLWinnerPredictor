
import pandas as pd
import requests
import json
import logging
from typing import Dict, Any
import numpy as np
import unicodedata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def predict(team_games: pd.DataFrame, opp_games: pd.DataFrame, next_game: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze historical data from CSVs using LM Studio model to predict match outcome and goals.
    
    Args:
        team_games (pd.DataFrame): TeamGamesTreated.csv (home team historical data)
        opp_games (pd.DataFrame): OppGamesTreated.csv (away team historical data)
        next_game (pd.DataFrame): NextGame.csv (upcoming match odds and details)
    
    Returns:
        Dict containing match details and predictions with explanations
    """
    try:
        # Extract match details
        home_team = next_game['HomeTeam'].iloc[0]
        away_team = next_game['AwayTeam'].iloc[0]
        match = f"{home_team} vs {away_team}"
        logger.info(f"Analyzing match: {match}")
        
        # Log CSV contents
        logger.info(f"TeamGamesTreated.csv columns: {list(team_games.columns)}")
        logger.info(f"TeamGamesTreated.csv HomeTeam values: {team_games['HomeTeam'].unique().tolist()}")
        logger.info(f"OppGamesTreated.csv columns: {list(opp_games.columns)}")
        logger.info(f"OppGamesTreated.csv AwayTeam values: {opp_games['AwayTeam'].unique().tolist()}")
        logger.info(f"NextGame.csv row: {next_game.to_dict(orient='records')[0]}")
        
        # Summarize team data
        team_stats = compute_team_stats(team_games, home_team, is_home=True)
        opp_stats = compute_team_stats(opp_games, away_team, is_home=False)
        odds_stats = compute_odds_stats(next_game)
        
        # Convert numpy types to Python types
        team_stats = convert_numpy_types(team_stats)
        opp_stats = convert_numpy_types(opp_stats)
        odds_stats = convert_numpy_types(odds_stats)
        
        # Log data summary
        logger.info(f"Home Team ({home_team}) Stats: {json.dumps(team_stats, indent=2)}")
        logger.info(f"Away Team ({away_team}) Stats: {json.dumps(opp_stats, indent=2)}")
        logger.info(f"Odds Stats: {json.dumps(odds_stats, indent=2)}")
        
        # Check for empty stats
        if team_stats['total_games'] == 0 or opp_stats['total_games'] == 0:
            logger.warning("Empty stats detected. Predictions may be unreliable.")
        
        # Create prompt for LM Studio
        prompt = create_lm_prompt(team_stats, opp_stats, odds_stats, home_team, away_team)
        logger.info(f"LM Studio Prompt:\n{prompt}")
        
        # Query LM Studio model
        model_response = query_lm_studio(prompt)
        logger.info(f"LM Studio Response:\n{model_response}")
        
        # Parse model response
        predictions = parse_model_response(model_response, match)
        
        return {
            "match": match,
            "prediction": predictions
        }
    
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return {
            "match": f"{home_team} vs {away_team}",
            "prediction": {
                "error": f"Prediction failed: {str(e)}"
            }
        }

def convert_numpy_types(data: Dict) -> Dict:
    """
    Convert numpy types to Python native types for JSON serialization.
    
    Args:
        data: Dictionary containing possible numpy types
    
    Returns:
        Dictionary with converted types
    """
    for key, value in data.items():
        if isinstance(value, (np.integer, np.floating)):
            data[key] = value.item()
        elif isinstance(value, np.ndarray):
            data[key] = value.tolist()
        elif pd.isna(value):
            data[key] = 0  # Replace NaN with 0
    return data

def compute_team_stats(df: pd.DataFrame, team: str, is_home: bool) -> Dict[str, Any]:
    """
    Compute statistics from team dataframe based on historical data.
    
    Args:
        df: DataFrame with team data
        team: Team name
        is_home: True if home team, False if away team
    
    Returns:
        Dictionary with team statistics
    """
    stats = {}
    try:
        # Normalize team name for matching
        def normalize_team_name(name: str) -> str:
            # Remove accents, convert to lowercase, strip whitespace
            name = ''.join(c for c in unicodedata.normalize('NFD', name)
                          if unicodedata.category(c) != 'Mn')
            return name.lower().strip()
        
        team_norm = normalize_team_name(team)
        logger.info(f"Searching for team: {team} (normalized: {team_norm})")
        
        # Filter games (home or away)
        if is_home:
            games = df[df['HomeTeam'].apply(normalize_team_name) == team_norm].copy()
            stats['context'] = 'home'
            logger.info(f"Found {len(games)} home games for {team}")
            stats['goals_scored_avg'] = games['FTHG'].mean() if 'FTHG' in games.columns and len(games) > 0 else 0
            stats['goals_conceded_avg'] = games['FTAG'].mean() if 'FTAG' in games.columns and len(games) > 0 else 0
        else:
            games = df[df['AwayTeam'].apply(normalize_team_name) == team_norm].copy()
            stats['context'] = 'away'
            logger.info(f"Found {len(games)} away games for {team}")
            stats['goals_scored_avg'] = games['FTAG'].mean() if 'FTAG' in games.columns and len(games) > 0 else 0
            stats['goals_conceded_avg'] = games['FTHG'].mean() if 'FTHG' in games.columns and len(games) > 0 else 0
        
        # Win/Draw/Loss rates
        if 'FTR' in games.columns:
            total_games = len(games)
            stats['win_rate'] = len(games[games['FTR'] == ('H' if is_home else 'A')]) / total_games if total_games > 0 else 0
            stats['draw_rate'] = len(games[games['FTR'] == 'D']) / total_games if total_games > 0 else 0
            stats['loss_rate'] = len(games[games['FTR'] == ('A' if is_home else 'H')]) / total_games if total_games > 0 else 0
        else:
            stats['win_rate'] = 0
            stats['draw_rate'] = 0
            stats['loss_rate'] = 0
        
        stats['total_games'] = len(games)
        stats['avg_total_goals'] = (stats['goals_scored_avg'] + stats['goals_conceded_avg']) if stats['total_games'] > 0 else 0
        
        return stats
    
    except Exception as e:
        logger.error(f"Error computing stats for {team}: {str(e)}")
        return {
            "context": "home" if is_home else "away",
            "goals_scored_avg": 0,
            "goals_conceded_avg": 0,
            "win_rate": 0,
            "draw_rate": 0,
            "loss_rate": 0,
            "total_games": 0,
            "avg_total_goals": 0
        }

def compute_odds_stats(next_game: pd.DataFrame) -> Dict[str, Any]:
    """
    Extract odds statistics from NextGame.csv.
    
    Args:
        next_game: DataFrame with next game data
    
    Returns:
        Dictionary with odds statistics
    """
    try:
        stats = {
            "home_odds": float(next_game['B365H'].iloc[0]) if 'B365H' in next_game.columns else 0,
            "draw_odds": float(next_game['B365D'].iloc[0]) if 'B365D' in next_game.columns else 0,
            "away_odds": float(next_game['B365A'].iloc[0]) if 'B365A' in next_game.columns else 0,
            "over_2_5_odds": float(next_game['B365>2.5'].iloc[0]) if 'B365>2.5' in next_game.columns else 0,
            "under_2_5_odds": float(next_game['B365<2.5'].iloc[0]) if 'B365<2.5' in next_game.columns else 0
        }
        return stats
    except Exception as e:
        logger.error(f"Error computing odds stats: {str(e)}")
        return {
            "home_odds": 0,
            "draw_odds": 0,
            "away_odds": 0,
            "over_2_5_odds": 0,
            "under_2_5_odds": 0
        }

def create_lm_prompt(team_stats, opp_stats, odds_stats, home_team, away_team):
    prompt = f"""
I need your help analyzing an upcoming football match between {home_team} (playing at home) and {away_team} (playing away).

historical performance data from two separate CSV files:
1. "TeamGamesTreated.csv" - Contains {team_stats['total_games']} historical HOME matches where {home_team} played as the home team
2. "OppGamesTreated.csv" - Contains {opp_stats['total_games']} historical AWAY matches where {away_team} played as the away team

 statistics:

### {home_team} Home Performance:
- Games Played at Home: {team_stats['total_games']}
- Average Goals Scored at Home: {team_stats['goals_scored_avg']:.2f}
- Average Goals Conceded at Home: {team_stats['goals_conceded_avg']:.2f}
- Home Win Rate: {team_stats['win_rate']:.2%} 
- Home Draw Rate: {team_stats['draw_rate']:.2%}
- Home Loss Rate: {team_stats['loss_rate']:.2%}
- Average Total Goals per Home Game: {team_stats['avg_total_goals']:.2f}

### {away_team} Away Performance:
- Games Played Away: {opp_stats['total_games']}
- Average Goals Scored Away: {opp_stats['goals_scored_avg']:.2f}
- Average Goals Conceded Away: {opp_stats['goals_conceded_avg']:.2f}
- Away Win Rate: {opp_stats['win_rate']:.2%}
- Away Draw Rate: {opp_stats['draw_rate']:.2%}
- Away Loss Rate: {opp_stats['loss_rate']:.2%}
- Average Total Goals per Away Game: {opp_stats['avg_total_goals']:.2f}

### Betting Odds for Upcoming Match:
- {home_team} Win: {odds_stats['home_odds']:.2f} (very low odds indicating strong favorite)
- Draw: {odds_stats['draw_odds']:.2f}
- {away_team} Win: {odds_stats['away_odds']:.2f} (very high odds indicating significant underdog)

As a football analyst, please:
1. Predict the most likely match outcome (home win, draw, or away win)
2. Predict whether there will be over or under 2.5 total goals in the match

For each prediction, provide a clear reasoning based on the data.
Format your response exactly as:

Outcome: [Your specific prediction] because [your reasoning based on the statistics]
Goals: [Your specific over/under prediction] because [your reasoning based on the statistics]
"""
    return prompt

def query_lm_studio(prompt: str) -> str:
    """
    Query the LM Studio model via its local API with improved parameters.
    """
    try:
        url = "http://localhost:1234/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        
        # More detailed system prompt to enforce output format
        system_prompt = """You are a football match analyst specializing in using statistics to predict match outcomes.
Always format your predictions as:
Outcome: [Team] win/draw because [specific reason]
Goals: Over/Under 2.5 goals because [specific reason]

Never include reasoning tags like <think> in your responses. Always be definitive in your predictions."""
        
        payload = {
            "model": "meta-llama-3-8b-instruct",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,  # Increased token limit
            "temperature": 0.4,  # Lower temperature for more deterministic output
            "top_p": 0.95,      # Slightly restrict token sampling
            "stop": ["<think>", "</think>"]  # Stop generation if these tags appear
        }
        
        logger.info(f"Sending request to LM Studio: {json.dumps(payload, indent=2)}")
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 404:
            logger.error("LM Studio returned 404: Ensure a model is loaded and the model name is correct.")
            raise Exception("LM Studio 404: No model loaded or incorrect model name")
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    
    except Exception as e:
        logger.error(f"LM Studio query failed: {str(e)}")
        raise

def parse_model_response(response: str, match: str) -> Dict[str, str]:
    """
    Parse the LM Studio model's response into structured predictions.
    
    Args:
        response: Raw text response from the model
        match: Match name (e.g., "Alavés vs Valencia")
    
    Returns:
        Dictionary with outcome and goals predictions
    """
    try:
        # Initialize defaults
        predictions = {
            "outcome": f"No clear prediction for {match}.",
            "goals": "No clear goals prediction."
        }
        
        # Remove any <think> tags and anything between them
        clean_response = response
        if "<think>" in response and "</think>" in response:
            start_idx = response.find("<think>")
            end_idx = response.find("</think>") + len("</think>")
            clean_response = response[:start_idx] + response[end_idx:]
        
        # Split response into lines
        lines = clean_response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("Outcome:"):
                predictions["outcome"] = line.replace("Outcome:", "").strip()
            elif line.startswith("Goals:"):
                predictions["goals"] = line.replace("Goals:", "").strip()
            
        # If we still don't have predictions, look for outcome/goals in the response text
        if predictions["outcome"] == f"No clear prediction for {match}.":
            if "win" in clean_response.lower() or "victory" in clean_response.lower():
                # Extract a sentence containing prediction
                sentences = [s.strip() for s in clean_response.split('.')]
                for sentence in sentences:
                    if "win" in sentence.lower() or "victory" in sentence.lower():
                        predictions["outcome"] = sentence.strip() + "."
                        break
        
        if predictions["goals"] == "No clear goals prediction.":
            if "over 2.5" in clean_response.lower() or "under 2.5" in clean_response.lower():
                sentences = [s.strip() for s in clean_response.split('.')]
                for sentence in sentences:
                    if "over 2.5" in sentence.lower() or "under 2.5" in sentence.lower():
                        predictions["goals"] = sentence.strip() + "."
                        break
        
        return predictions
    
    except Exception as e:
        logger.error(f"Error parsing model response: {str(e)}")
        return {
            "outcome": f"Error parsing outcome for {match}.",
            "goals": "Error parsing goals prediction."
        }
        
        
def main():
    """
    Main function for testing prediction.py standalone.
    """
    try:
        # Load dataframes
        team_games = pd.read_csv("TeamGamesTreated.csv")
        opp_games = pd.read_csv("OppGamesTreated.csv")
        next_game = pd.read_csv("NextGame.csv")
        
        # Run prediction
        result = predict(team_games, opp_games, next_game)
        
        # Print results
        print(f"Match: {result['match']}")
        print("Predictions:")
        if "error" in result['prediction']:
            print(f"  Error: {result['prediction']['error']}")
        else:
            print(f"  Outcome: {result['prediction']['outcome']}")
            print(f"  Goals: {result['prediction']['goals']}")
    
    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()