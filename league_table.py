# league_table.py
# Functions for building league tables and updating team positions
import pandas as pd
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('league_table.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def extract_season_from_date(date_str: str, default_season: str = "2024/2025") -> str:
    """Extract season from a date string."""
    try:
        date = pd.to_datetime(date_str, dayfirst=True)
        year = date.year
        month = date.month
        season_start = year if month >= 7 else year - 1
        return f"{season_start}/{season_start + 1}"
    except Exception:
        logger.warning(f"Could not extract season from {date_str}, using default {default_season}")
        return default_season

def build_league_table_from_games(games_df: pd.DataFrame, league_name: str) -> pd.DataFrame:
    """Build a league table from game data."""
    try:
        teams = set(games_df['HomeTeam']).union(set(games_df['AwayTeam']))
        table = {
            'Team': [],
            'Played': [],
            'Won': [],
            'Drawn': [],
            'Lost': [],
            'GF': [],
            'GA': [],
            'GD': [],
            'Points': []
        }
        
        for team in teams:
            home_games = games_df[games_df['HomeTeam'] == team]
            away_games = games_df[games_df['AwayTeam'] == team]
            
            played = len(home_games) + len(away_games)
            won = len(home_games[home_games['FTR'] == 'H']) + len(away_games[away_games['FTR'] == 'A'])
            drawn = len(home_games[home_games['FTR'] == 'D']) + len(away_games[away_games['FTR'] == 'D'])
            lost = played - won - drawn
            gf = home_games['FTHG'].sum() + away_games['FTAG'].sum()
            ga = home_games['FTAG'].sum() + away_games['FTHG'].sum()
            gd = gf - ga
            points = won * 3 + drawn
            
            table['Team'].append(team)
            table['Played'].append(played)
            table['Won'].append(won)
            table['Drawn'].append(drawn)
            table['Lost'].append(lost)
            table['GF'].append(gf)
            table['GA'].append(ga)
            table['GD'].append(gd)
            table['Points'].append(points)
        
        table_df = pd.DataFrame(table)
        table_df = table_df.sort_values(by=['Points', 'GD', 'GF'], ascending=[False, False, False]).reset_index(drop=True)
        table_df['Position'] = table_df.index + 1
        
        #logger.info(f"Built league table for {league_name} with {len(teams)} teams")
        return table_df
    except Exception as e:
        logger.error(f"Error building league table: {str(e)}")
        raise

def add_positions_to_games(games_df: pd.DataFrame, league_name: str) -> pd.DataFrame:
    """Add HomePosition and AwayPosition columns based on games before each match in the same season."""
    try:
        result_df = games_df.copy()
        result_df['Date'] = pd.to_datetime(result_df['Date'], dayfirst=True, errors='coerce')
        result_df = result_df.dropna(subset=['Date', 'Season'])
        result_df = result_df.sort_values(by=['Season', 'Date'])
        
        result_df['HomePosition'] = 0
        result_df['AwayPosition'] = 0
        
        for season, season_games in result_df.groupby('Season'):
            season_games = season_games.sort_values('Date')
            prior_games = pd.DataFrame()
            
            for idx, row in season_games.iterrows():
                match_date = row['Date']
                prior_games = pd.concat([prior_games, season_games[season_games['Date'] < match_date]])
                
                if not prior_games.empty:
                    table = build_league_table_from_games(prior_games, f"{league_name}_{season}")
                    position_map = dict(zip(table['Team'], table['Position']))
                else:
                    position_map = {team: 0 for team in set(season_games['HomeTeam']).union(set(season_games['AwayTeam']))}
                
                result_df.at[idx, 'HomePosition'] = position_map.get(row['HomeTeam'], 0)
                result_df.at[idx, 'AwayPosition'] = position_map.get(row['AwayTeam'], 0)
        
        logger.info("Added position columns to games DataFrame")
        return result_df
    except Exception as e:
        logger.error(f"Error adding positions to games: {str(e)}")
        raise

def update_all_dataframes_with_positions(league_name: str) -> None:
    """Update all relevant CSV files with position columns."""
    try:
        for file in ['AllGames.csv', 'TeamGames.csv', 'OppGames.csv']:
            if os.path.exists(file):
                df = pd.read_csv(file)
                df = add_positions_to_games(df, league_name)
                df.to_csv(file, index=False)
                logger.info(f"Updated {file} with positions")
            else:
                logger.warning(f"{file} not found, skipping")
    except Exception as e:
        logger.error(f"Error updating dataframes with positions: {str(e)}")
        raise

def get_current_league_table(league_name: str, season: int) -> pd.DataFrame:
    """Get the current league table for a given season."""
    try:
        if not os.path.exists('AllGames.csv'):
            logger.error("AllGames.csv not found")
            return pd.DataFrame()
        
        games_df = pd.read_csv('AllGames.csv')
        games_df = games_df[games_df['Season'] == f"{season}/{season + 1}"]
        if games_df.empty:
            logger.warning(f"No games found for season {season}/{season + 1}")
            return pd.DataFrame()
        
        table_df = build_league_table_from_games(games_df, league_name)
        return table_df
    except Exception as e:
        logger.error(f"Error getting current league table: {str(e)}")
        return pd.DataFrame()

def update_next_game_with_latest_positions(league_name: str) -> None:
    """Update NextGame.csv with the latest team positions."""
    try:
        if not os.path.exists('NextGame.csv') or not os.path.exists('AllGames.csv'):
            logger.warning("NextGame.csv or AllGames.csv not found, skipping update")
            return
        
        next_game_df = pd.read_csv('NextGame.csv')
        games_df = pd.read_csv('AllGames.csv')
        table = build_league_table_from_games(games_df, league_name)
        
        position_map = dict(zip(table['Team'], table['Position']))
        
        next_game_df['HomePosition'] = next_game_df['HomeTeam'].map(position_map).fillna(0).astype(int)
        next_game_df['AwayPosition'] = next_game_df['AwayTeam'].map(position_map).fillna(0).astype(int)
        
        next_game_df.to_csv('NextGame.csv', index=False)
        logger.info("Updated NextGame.csv with latest positions")
    except Exception as e:
        logger.error(f"Error updating NextGame.csv: {str(e)}")
        raise

def get_team_position_for_matchday(league_name: str, team: str, season: int, matchday: int) -> str:
    """Get team position for a specific matchday in the given season."""
    try:
        if not os.path.exists('AllGames.csv'):
            logger.error("AllGames.csv not found")
            return "Unknown"
        
        games_df = pd.read_csv('AllGames.csv')
        games_df = games_df[games_df['Season'] == f"{season}/{season + 1}"]
        if games_df.empty:
            logger.warning(f"No games found for {league_name} season {season}/{season + 1}")
            return "Unknown"
        
        # Convert dates and sort
        games_df['Date'] = pd.to_datetime(games_df['Date'], dayfirst=True, errors='coerce')
        games_df = games_df.dropna(subset=['Date']).sort_values('Date')
        
        # Group by date to estimate matchdays
        games_df['Matchday'] = (games_df.groupby('Date').ngroup() // (len(set(games_df['HomeTeam'])) // 2)) + 1
        matchday_games = games_df[games_df['Matchday'] <= matchday]
        
        if matchday_games.empty:
            logger.warning(f"No games found up to matchday {matchday}")
            return "Unknown"
        
        table = build_league_table_from_games(matchday_games, f"{league_name}_Matchday{matchday}")
        team_row = table[table['Team'] == team]
        
        return str(team_row['Position'].iloc[0]) if not team_row.empty else "Unknown"
    except Exception as e:
        logger.error(f"Error getting position for matchday: {str(e)}")
        return "Unknown"