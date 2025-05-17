# treatment.py
# Functions for processing football match data and adding required columns
import pandas as pd
import numpy as np
import logging
from typing import Optional
from datetime import datetime
import url
import requests
import os
from tenacity import retry, stop_after_attempt, wait_fixed
from io import StringIO

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('treatment.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def validate_club(club: str, league: str) -> bool:
    """Validate if a club exists in the specified league."""
    if league not in url.clubs_by_league or club not in url.clubs_by_league[league]:
        logger.error(f"Club {club} not found in {league}")
        return False
    return True

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_csv(url_path: str) -> pd.DataFrame:
    """Fetch CSV from URL with retry logic."""
    logger.info(f"Attempting to fetch {url_path}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url_path, headers=headers, timeout=10)
        logger.info(f"Response status for {url_path}: {response.status_code}")
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), encoding='latin-1')
        return df
    except Exception as e:
        logger.error(f"Error in fetch_csv for {url_path}: {str(e)}")
        raise

def cut_useless_rows(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Process a DataFrame to keep only relevant columns and add WeekDay."""
    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.error("Input is not a valid DataFrame or is empty")
        return None
    
    essential_columns = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
    optional_columns = [
        'B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA',
        'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA',
        'B365>2.5', 'B365<2.5', 'Max<2.5', 'Max>2.5',
        'Avg<2.5', 'Avg>2.5'
    ]
    
    # Check essential columns
    missing_essential = [col for col in essential_columns if col not in df.columns]
    if missing_essential:
        logger.error(f"Missing essential columns: {', '.join(missing_essential)}")
        return None
    
    # Keep available columns
    columns_to_keep = essential_columns + [col for col in optional_columns if col in df.columns]
    df_selected = df[columns_to_keep].copy()
    
    # Drop rows with NaN in essential columns
    df_selected = df_selected.dropna(subset=essential_columns)
    
    if df_selected.empty:
        logger.error("DataFrame is empty after dropping NaN in essential columns")
        return None
    
    # Add WeekDay
    try:
        df_selected['WeekDay'] = df_selected['Date'].apply(get_day_of_week)
        if df_selected['WeekDay'].isna().all():
            logger.warning("Failed to parse any dates")
            return None
        logger.debug(f"Processed DataFrame head:\n{df_selected.head().to_string()}")
    except ValueError as e:
        logger.error(f"Error processing dates: {e}")
        return None
    
    return df_selected

def filter_club_games(var_club_name: str, df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Filter games for a specific club (home or away)."""
    if df is None or df.empty:
        logger.error("Input DataFrame for filtering is None or empty")
        return None
    return df.loc[(df['HomeTeam'] == var_club_name) | (df['AwayTeam'] == var_club_name)].copy()

def process_all_games(season_start: int, season_end: int, league: str) -> Optional[str]:
    """Process all matches for a range of seasons and save to AllGames.csv."""
    if league not in url.available_leagues:
        logger.error(f"League {league} not supported")
        return f"Error: League {league} not supported"
    
    dfs = []
    for season in range(season_start, season_end + 1):
        csvs_path = url.file_path_builder(league, season, season)
        logger.info(f"Fetching data for season {season}/{season + 1}: {csvs_path}")
        
        # Try fetching from URLs
        for path in csvs_path:
            try:
                df = fetch_csv(path)
                logger.info(f"Raw data rows from {path}: {len(df)}")
                logger.debug(f"Columns: {df.columns.tolist()}")
                df = cut_useless_rows(df)
                if df is not None and not df.empty:
                    df['Season'] = f"{season}/{season + 1}"
                    dfs.append(df)
                    logger.info(f"Processed {len(df)} rows for season {season}/{season + 1}")
                else:
                    logger.warning(f"No valid data from {path}")
            except Exception as e:
                logger.error(f"Failed to fetch/process {path}: {e}")
    
    # Fallback to local file for the latest season
    if not dfs and season_end == 2024:
        local_file = "I1.csv"
        if os.path.exists(local_file):
            logger.info(f"Falling back to local file {local_file} for season 2024/2025")
            try:
                df = pd.read_csv(local_file, encoding='latin-1')
                logger.info(f"Raw data rows from {local_file}: {len(df)}")
                logger.debug(f"Columns: {df.columns.tolist()}")
                df = cut_useless_rows(df)
                if df is not None and not df.empty:
                    df['Season'] = "2024/2025"
                    dfs.append(df)
                    logger.info(f"Processed {len(df)} rows from {local_file}")
                else:
                    logger.warning(f"No valid data from {local_file}")
            except Exception as e:
                logger.error(f"Failed to process {local_file}: {e}")
        else:
            logger.error(f"No local file {local_file} found")
    
    if not dfs:
        logger.error(f"No valid games found for {league}")
        return f"Error: No games found"
    
    df_concatenated = pd.concat(dfs).drop_duplicates(
        subset=['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
    )
    if df_concatenated.empty:
        logger.error("Concatenated DataFrame is empty")
        return f"Error: Concatenated DataFrame is empty"
    
    output_path = os.path.join(os.getcwd(), "AllGames.csv")
    df_concatenated.to_csv(output_path, index=False)
    logger.info(f"Saved {len(df_concatenated)} matches to {output_path}")
    logger.debug(f"AllGames.csv columns: {df_concatenated.columns.tolist()}")
    return None

def handler(season: int, league: str, star_club: str, opp_club: str) -> Optional[str]:
    """Process historical match data for two clubs and all matches across multiple seasons."""
    pd.set_option('display.max_columns', None)
    
    # Process all games for seasons 2020 to 2024
    error = process_all_games(2020, 2024, league)
    if error:
        logger.error(f"Failed to process all games: {error}")
        return error
    
    # Validate clubs
    if not validate_club(star_club, league):
        return f"Error: {star_club} not found in {league}"
    if not validate_club(opp_club, league):
        return f"Error: {opp_club} not found in {league}"
    
    dfs_club = []
    dfs_opp = []
    
    # Fetch data for each season
    for var_season in range(2020, 2025):
        csvs_path = url.file_path_builder(league, var_season, var_season)
        logger.info(f"Processing club data for season {var_season}/{var_season + 1}: {csvs_path}")
        
        for path in csvs_path:
            try:
                df = fetch_csv(path)
                logger.info(f"Raw data rows: {len(df)}")
                logger.debug(f"Columns: {df.columns.tolist()}")
                df = cut_useless_rows(df)
                if df is None or df.empty:
                    logger.warning(f"No valid data from {path}")
                    continue
                
                df['Season'] = f"{var_season}/{var_season + 1}"
                df_club = filter_club_games(star_club, df)
                df_opp = filter_club_games(opp_club, df)
                
                if df_club is not None and not df_club.empty:
                    dfs_club.append(df_club)
                    logger.info(f"Processed {len(df_club)} games for {star_club} from season {var_season}/{var_season + 1}")
                if df_opp is not None and not df_opp.empty:
                    dfs_opp.append(df_opp)
                    logger.info(f"Processed {len(df_opp)} games for {opp_club} from season {var_season}/{var_season + 1}")
            except Exception as e:
                logger.error(f"Failed to process {path}: {e}")
    
    # Fallback to local file for 2024/2025
    if not dfs_club or not dfs_opp:
        local_file = "I1.csv"
        if os.path.exists(local_file):
            logger.info(f"Falling back to local file {local_file} for season 2024/2025")
            try:
                df = pd.read_csv(local_file, encoding='latin-1')
                df = cut_useless_rows(df)
                if df is not None and not df.empty:
                    df['Season'] = "2024/2025"
                    df_club = filter_club_games(star_club, df)
                    df_opp = filter_club_games(opp_club, df)
                    if df_club is not None and not df_club.empty:
                        dfs_club.append(df_club)
                    if df_opp is not None and not df_opp.empty:
                        dfs_opp.append(df_opp)
            except Exception as e:
                logger.error(f"Failed to process {local_file}: {e}")
    
    if not dfs_club or not dfs_opp:
        logger.error(f"No games found for {star_club} or {opp_club}")
        return f"Error: No games found for {star_club} or {opp_club}"
    
    df_club_concatenated = pd.concat(dfs_club).drop_duplicates(
        subset=['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
    )
    df_opp_concatenated = pd.concat(dfs_opp).drop_duplicates(
        subset=['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
    )
    
    df_club_concatenated.to_csv("TeamGames.csv", index=False)
    df_opp_concatenated.to_csv("OppGames.csv", index=False)
    logger.info("Saved TeamGames.csv and OppGames.csv")
    
    return None

def add_total_goals_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add TotalGoals column by summing FTHG and FTAG."""
    required_cols = ['FTHG', 'FTAG']
    if df is None or df.empty or not all(col in df.columns for col in required_cols):
        logger.error("Missing required columns for TotalGoals")
        raise ValueError("Missing required columns")
    
    if not all(df[col].dtype.kind in 'iuf' for col in required_cols):
        logger.error("FTHG and FTAG must be numeric")
        raise ValueError("FTHG and FTAG must be numeric")
    
    df['TotalGoals'] = df['FTHG'] + df['FTAG']
    df.loc[df[required_cols].isna().any(axis=1), 'TotalGoals'] = np.nan
    
    logger.info("Added TotalGoals column")
    return df

def add_FTRodds_feedback(df: pd.DataFrame) -> pd.DataFrame:
    """Add FTRodds_feedback indicating if the favorite outcome matches the actual outcome."""
    required_cols = ['FTR', 'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA']
    if df is None or df.empty or not all(col in df.columns for col in required_cols):
        logger.warning("Missing required columns for FTRodds_feedback, skipping")
        df['FTRodds_feedback'] = 'NA'
        return df
    
    df['FTRodds_feedback'] = 'NA'
    valid = (~df[required_cols[1:]].isna().any(axis=1)) & (df['FTR'].isin(['H', 'A', 'D']))
    
    if valid.any():
        odds = df.loc[valid, ['MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA']]
        min_odds = odds.min(axis=1)
        favorites = odds.eq(min_odds, axis=0).apply(
            lambda x: [k[-1] for k in x.index[x] if k.startswith(('Max', 'Avg'))], axis=1
        )
        df.loc[valid, 'FTRodds_feedback'] = df.loc[valid, 'FTR'].combine(
            favorites, lambda ftr, fav: str(ftr in fav)
        )
    
    logger.info("Added FTRodds_feedback column")
    return df

def add_Goalsodds_feedback(df: pd.DataFrame) -> pd.DataFrame:
    """Add Goalsodds_feedback indicating if the favorite goals outcome matches the actual."""
    required_cols = ['FTHG', 'FTAG', 'Max>2.5', 'Max<2.5', 'Avg>2.5', 'Avg<2.5']
    if df is None or df.empty or not all(col in df.columns for col in required_cols):
        logger.warning("Missing required columns for Goalsodds_feedback, skipping")
        df['Goalsodds_feedback'] = 'NA'
        return df
    
    df['Goalsodds_feedback'] = 'NA'
    valid = (~df[required_cols].isna().any(axis=1))
    
    if valid.any():
        total_goals = df.loc[valid, 'FTHG'] + df.loc[valid, 'FTAG']
        actual_outcome = np.where(total_goals > 2.5, 'Over', 'Under')
        odds = df.loc[valid, ['Max>2.5', 'Max<2.5', 'Avg>2.5', 'Avg<2.5']]
        min_odds = odds.min(axis=1)
        outcome_map = {'Max>2.5': 'Over', 'Avg>2.5': 'Over', 'Max<2.5': 'Under', 'Avg<2.5': 'Under'}
        favorites = odds.eq(min_odds, axis=0).apply(
            lambda x: [outcome_map[k] for k in x.index[x]], axis=1
        )
        df.loc[valid, 'Goalsodds_feedback'] = [
            str(outcome in favs) for outcome, favs in zip(actual_outcome, favorites)
        ]
    
    logger.info("Added Goalsodds_feedback column")
    return df

def treatment_of_date(df: pd.DataFrame) -> pd.DataFrame:
    """Convert dates and extract Day, Month, Year, and Day_of_week."""
    if df is None or 'Date' not in df.columns:
        logger.error("No Date column found in DataFrame")
        raise ValueError("No Date column found")
    
    date_formats = ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d']
    for fmt in date_formats:
        try:
            df['Date'] = pd.to_datetime(df['Date'], format=fmt, dayfirst=True, errors='coerce')
            break
        except ValueError:
            continue
    else:
        logger.error("Could not parse dates")
        raise ValueError("Could not parse dates")
    
    df = df.dropna(subset=['Date'])
    df['Day'] = df['Date'].dt.day
    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    df['Day_of_week'] = df['Date'].dt.dayofweek
    df = df.drop(columns=['Date', 'WeekDay'], errors='ignore')
    
    logger.info("Processed dates and added Day, Month, Year, Day_of_week columns")
    return df

def get_day_of_week(date_str: str) -> int:
    """Get the day of the week (0=Mon, 6=Sun) from a date string."""
    try:
        date_formats = ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d']
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(str(date_str), fmt)
                return date_obj.weekday()
            except ValueError:
                continue
        raise ValueError(f"Cannot parse date {date_str}")
    except Exception as e:
        logger.error(f"Error parsing date {date_str}: {e}")
        raise  ValueError(f"Error parsing date {date_str}: {e}")
def extract_season_from_date(date_str: str) -> Optional[str]:   
    """Extract the season from a date string."""
    try:
        date_obj = pd.to_datetime(date_str, format='%d/%m/%Y', errors='coerce')
        if pd.isna(date_obj):
            return None
        year = date_obj.year
        month = date_obj.month
        if month >= 8:  # August or later
            return f"{year}/{year + 1}"
        else:  # Before August
            return f"{year - 1}/{year}"
    except Exception as e:
        logger.error(f"Error extracting season from date {date_str}: {e}")
        return None
    
    
def treatment_of_date(df: pd.DataFrame) -> pd.DataFrame:
    """Process Date column and add Day, Month, Year, Day_of_week columns."""
    try:
        result_df = df.copy()
        result_df['Date'] = pd.to_datetime(result_df['Date'], dayfirst=True, errors='coerce')
        
        # Initialize columns
        result_df['Day'] = None
        result_df['Month'] = None
        result_df['Year'] = None
        result_df['Day_of_week'] = None
        
        # Extract components
        valid_dates = result_df['Date'].notna()
        result_df.loc[valid_dates, 'Day'] = result_df.loc[valid_dates, 'Date'].dt.day
        result_df.loc[valid_dates, 'Month'] = result_df.loc[valid_dates, 'Date'].dt.month
        result_df.loc[valid_dates, 'Year'] = result_df.loc[valid_dates, 'Date'].dt.year
        result_df.loc[valid_dates, 'Day_of_week'] = result_df.loc[valid_dates, 'Date'].dt.day_name()
        
        # Convert to integers, fill NA with 0
        result_df['Day'] = pd.to_numeric(result_df['Day'], errors='coerce').fillna(0).astype(int)
        result_df['Month'] = pd.to_numeric(result_df['Month'], errors='coerce').fillna(0).astype(int)
        result_df['Year'] = pd.to_numeric(result_df['Year'], errors='coerce').fillna(0).astype(int)
        
        logger.info("Processed dates and added Day, Month, Year, Day_of_week columns")
        return result_df
    except Exception as e:
        logger.error(f"Error processing dates: {str(e)}")
        return df
