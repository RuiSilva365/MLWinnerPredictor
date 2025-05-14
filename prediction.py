
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

def create_lm_prompt(team_stats: Dict, opp_stats: Dict, odds_stats: Dict, home_team: str, away_team: str) -> str:
    """
    Create a prompt for the LM Studio model.
    
    Args:
        team_stats: Home team statistics
        opp_stats: Away team statistics
        odds_stats: Odds statistics
        home_team: Home team name
        away_team: Away team name
    
    Returns:
        String prompt for the model
    """
    prompt = f"""
You are a football match analyst. Analyze the following historical data for the upcoming match between {home_team} (home) and {away_team} (away) to predict the match outcome and total goals. Focus on insights from the data, such as team performance, goal trends, or odds value. Provide two outputs:
1. A prediction for the match outcome (e.g., "{home_team} might win because...") with a valid observation based on the data.
2. A prediction for total goals (e.g., "Over 2.5 goals is likely because...") with a valid observation based on the data.

### Historical Data Summary:
**{home_team} (Home) Stats (based on past home games):**
- Games Played: {team_stats['total_games']}
- Average Goals Scored: {team_stats['goals_scored_avg']:.2f}
- Average Goals Conceded: {team_stats['goals_conceded_avg']:.2f}
- Win Rate: {team_stats['win_rate']:.2%} 
- Draw Rate: {team_stats['draw_rate']:.2%}
- Loss Rate: {team_stats['loss_rate']:.2%}
- Average Total Goals per Game: {team_stats['avg_total_goals']:.2f}

**{away_team} (Away) Stats (based on past away games):**
- Games Played: {opp_stats['total_games']}
- Average Goals Scored: {opp_stats['goals_scored_avg']:.2f}
- Average Goals Conceded: {opp_stats['goals_conceded_avg']:.2f}
- Win Rate: {opp_stats['win_rate']:.2%}
- Draw Rate: {opp_stats['draw_rate']:.2%}
- Loss Rate: {opp_stats['loss_rate']:.2%}
- Average Total Goals per Game: {opp_stats['avg_total_goals']:.2f}

**Betting Odds for Upcoming Match:**
- {home_team} Win: {odds_stats['home_odds']:.2f}
- Draw: {odds_stats['draw_odds']:.2f}
- {away_team} Win: {odds_stats['away_odds']:.2f}
- Over 2.5 Goals: {odds_stats['over_2_5_odds']:.2f}
- Under 2.5 Goals: {odds_stats['under_2_5_odds']:.2f}

### Instructions:
- Analyze the historical data to identify patterns (e.g., strong home performance, high-scoring games).
- Provide a concise prediction for the match outcome with a specific reason based on the data.
- Provide a concise prediction for over/under 2.5 goals with a specific reason based on the data.
- Format the response as:
  - Outcome: [Your prediction and reason]
  - Goals: [Your prediction and reason]
"""
    return prompt

def query_lm_studio(prompt: str) -> str:
    """
    Query the LM Studio model via its local API.
    
    Args:
        prompt: Input prompt for the model
    
    Returns:
        Model's text response
    """
    try:
        url = "http://localhost:1234/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "phi-4-reasoning-plus",  # Replace with your model name (e.g., "phi-2", "llama-7b-hf")
            "messages": [
                {"role": "system", "content": "You are a football match analyst."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 200,
            "temperature": 0.7
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
        
        # Split response into lines
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("Outcome:"):
                predictions["outcome"] = line.replace("Outcome:", "").strip()
            elif line.startswith("Goals:"):
                predictions["goals"] = line.replace("Goals:", "").strip()
        
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