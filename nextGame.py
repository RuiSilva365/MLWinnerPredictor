# nextGame.py
# Module for handling next game data collection and formatting
import pandas as pd
import logging
import os
from datetime import datetime
import url
import treatment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('nextGame.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def create_next_game(star_club: str, opp_club: str, league: str, game_date: str, season: int) -> None:
    """
    Create NextGame.csv for the next game between two clubs with odds from OddsPortal.
    
    Args:
        star_club (str): Main club to analyze.
        opp_club (str): Opponent club to analyze.
        league (str): League name.
        game_date (str): Date of the game in DD/MM/YYYY format.
        season (int): Season start year (e.g., 2024 for 2024/2025).
    """
    try:
        # Attempt to find the next game with odds
        game_info = url.find_next_game_with_odds(star_club, opp_club, league, game_date)
        date_str = game_info['date']
        home_team = game_info['home_team']
        away_team = game_info['away_team']
        odds_data = game_info.get('odds', {})
        
        # Define full column set for NextGame.csv
        columns = [
            'Date', 'HomeTeam', 'AwayTeam', #'FTHG', 'FTAG', 'FTR',
            'Season',
            'B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA',
            'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA',
            'B365>2.5', 'B365<2.5', 'Max>2.5', 'Max<2.5', 'Avg>2.5', 'Avg<2.5',
            'TotalGoals', #'FTRodds_feedback', 'Goalsodds_feedback',
            'Day', 'Month', 'Year', 'Day_of_week',
            'Temperature', 'Precipitation', 'WeatherCode', 'Weather',
            'HomePosition', 'AwayPosition'
        ]
        
        # Create DataFrame with all required columns
        next_game_df = pd.DataFrame([{
            'Date': date_str,
            'HomeTeam': home_team,
            'AwayTeam': away_team,
            'FTHG': None,
            'FTAG': None,
            'FTR': None,
            'Season': f"{season}/{season + 1}",
            'B365H': odds_data.get('B365H', 2.0),
            'B365D': odds_data.get('B365D', 3.5),
            'B365A': odds_data.get('B365A', 3.0),
            'BWH': odds_data.get('BWH', 2.1),
            'BWD': odds_data.get('BWD', 3.4),
            'BWA': odds_data.get('BWA', 2.9),
            'MaxH': odds_data.get('MaxH', 2.2),
            'MaxD': odds_data.get('MaxD', 3.6),
            'MaxA': odds_data.get('MaxA', 3.1),
            'AvgH': odds_data.get('AvgH', 2.1),
            'AvgD': odds_data.get('AvgD', 3.5),
            'AvgA': odds_data.get('AvgA', 3.0),
            'B365>2.5': odds_data.get('B365>2.5', 1.9),
            'B365<2.5': odds_data.get('B365<2.5', 2.1),
            'Max>2.5': odds_data.get('Max>2.5', 2.0),
            'Max<2.5': odds_data.get('Max<2.5', 2.2),
            'Avg>2.5': odds_data.get('Avg>2.5', 1.95),
            'Avg<2.5': odds_data.get('Avg<2.5', 2.15),
            'TotalGoals': None,
            'FTRodds_feedback': 'NA',
            'Goalsodds_feedback': 'NA',
            'Day': None,
            'Month': None,
            'Year': None,
            'Day_of_week': None,
            'Temperature': None,
            'Precipitation': None,
            'WeatherCode': None,
            'Weather': 'Unknown',
            'HomePosition': 0,
            'AwayPosition': 0
        }], columns=columns)
        
        # Process date components
        next_game_df = treatment.treatment_of_date(next_game_df)
        
        # Save NextGame.csv
        next_game_df.to_csv("NextGame.csv", index=False)
        logger.info(f"Created NextGame.csv for {home_team} vs {away_team} on {date_str}")
    
    except Exception as e:
        logger.error(f"Error creating NextGame.csv: {str(e)}")
        create_fallback_next_game_csv(star_club, opp_club, game_date, season)

def create_fallback_next_game_csv(star_club: str, opp_club: str, game_date: str, season: int) -> None:
    """
    Create a fallback NextGame.csv with minimal data and placeholder odds.
    
    Args:
        star_club (str): Main club to analyze.
        opp_club (str): Opponent club to analyze.
        game_date (str): Date of the game in DD/MM/YYYY format.
        season (int): Season start year (e.g., 2024 for 2024/2025).
    """
    try:
        columns = [
            'Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'Season',
            'B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA',
            'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA',
            'B365>2.5', 'B365<2.5', 'Max>2.5', 'Max<2.5', 'Avg>2.5', 'Avg<2.5',
            'TotalGoals', 'FTRodds_feedback', 'Goalsodds_feedback',
            'Day', 'Month', 'Year', 'Day_of_week',
            'Temperature', 'Precipitation', 'WeatherCode', 'Weather',
            'HomePosition', 'AwayPosition'
        ]
        fallback_df = pd.DataFrame([{
            'Date': game_date,
            'HomeTeam': star_club,
            'AwayTeam': opp_club,
            'FTHG': None,
            'FTAG': None,
            'FTR': None,
            'Season': f"{season}/{season + 1}",
            'B365H': 2.0,
            'B365D': 3.5,
            'B365A': 3.0,
            'BWH': 2.1,
            'BWD': 3.4,
            'BWA': 2.9,
            'MaxH': 2.2,
            'MaxD': 3.6,
            'MaxA': 3.1,
            'AvgH': 2.1,
            'AvgD': 3.5,
            'AvgA': 3.0,
            'B365>2.5': 1.9,
            'B365<2.5': 2.1,
            'Max>2.5': 2.0,
            'Max<2.5': 2.2,
            'Avg>2.5': 1.95,
            'Avg<2.5': 2.15,
            'TotalGoals': None,
            'FTRodds_feedback': 'NA',
            'Goalsodds_feedback': 'NA',
            'Day': None,
            'Month': None,
            'Year': None,
            'Day_of_week': None,
            'Temperature': None,
            'Precipitation': None,
            'WeatherCode': None,
            'Weather': 'Unknown',
            'HomePosition': 0,
            'AwayPosition': 0
        }], columns=columns)
        
        # Process date components
        fallback_df = treatment.treatment_of_date(fallback_df)
        
        # Save fallback CSV
        fallback_df.to_csv("NextGame.csv", index=False)
        logger.info(f"Created fallback NextGame.csv for {star_club} vs {opp_club} on {game_date}")
    
    except Exception as e:
        logger.error(f"Error creating fallback NextGame.csv: {str(e)}")

def list_upcoming_fixtures(league: str) -> list:
    """
    List all upcoming fixtures for a league.
    
    Args:
        league (str): League name.
    
    Returns:
        list: List of fixture dictionaries.
    """
    fixtures = url.get_league_fixtures(league)
    
    if not fixtures:
        logger.warning(f"No upcoming fixtures found for {league}")
        return []
    
    return fixtures

def select_game_by_index(fixtures: list, index: int) -> dict:
    """
    Select a game from the fixtures list by index.
    
    Args:
        fixtures (list): List of fixture dictionaries.
        index (int): Index of the fixture to select.
    
    Returns:
        dict: Selected fixture, or None if index is out of range.
    """
    if 0 <= index < len(fixtures):
        return fixtures[index]
    return None