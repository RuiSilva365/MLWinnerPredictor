import pandas as pd
import numpy as np
import logging
from typing import Optional
from datetime import datetime
import url
try:
    from tenacity import retry, stop_after_attempt, wait_fixed # type: ignore
except ImportError:
    retry = lambda func: func  # Fallback if tenacity is not installed

# Configure logging for production
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_club(club, league):
    """Validate if a club exists in the specified league."""
    if league not in url.clubs_by_league or club not in url.clubs_by_league[league]:
        return False
    return True

def handler(season, star_league, star_club, opp_club):
    """
    Process historical match data for two clubs and save to CSV.
    
    Args:
        season (int): Starting season (e.g., 2023 for 2023/2024).
        star_league (str): League name (e.g., 'Premier League').
        star_club (str): Main club to analyze.
        opp_club (str): Opponent club to analyze.
    
    Returns:
        str: Error message if any, else None.
    """
    pd.set_option('display.max_columns', None)
    
    # Validate inputs
    if not validate_club(star_club, star_league):
        return f"Error: {star_club} not found in {star_league}"
    if not validate_club(opp_club, star_league):
        return f"Error: {opp_club} not found in {star_league}"
    
    if star_league not in url.file_path_leagues:
        return f"Error: League {star_league} not supported"
    
    var_firstseason = int(season)
    var_lastseason = 2425  # Fixed to 2024/2025
    csvs_path = url.file_path_builder(star_league, var_firstseason, var_lastseason)
    
    if not csvs_path:
        return f"Error: No CSV files found for {star_league} between {var_firstseason} and {var_lastseason}"
    
    dfs_club = []
    dfs_opp = []
    
    for path in csvs_path:
        df = cut_useless_rows(path)
        if df is None:
            return f"Error: Failed to process CSV at {path}"
        
        # Filter games for each club
        df_club = filter_club_games(star_club, df)
        df_opp = filter_club_games(opp_club, df)
        
        if df_club is not None and not df_club.empty:
            dfs_club.append(df_club)
        if df_opp is not None and not df_opp.empty:
            dfs_opp.append(df_opp)
    
    if not dfs_club or not dfs_opp:
        return f"Error: No games found for {star_club} or {opp_club}"
    
    # Concatenate and save
    df_club_concatenated = pd.concat(dfs_club)
    df_opp_concatenated = pd.concat(dfs_opp)
    
    df_club_concatenated.to_csv("TeamGames.csv", index=False)
    df_opp_concatenated.to_csv("OppGames.csv", index=False)
    
    return None

def cut_useless_rows(file):
    """
    Process a CSV file to keep only relevant columns and add day of week.
    
    Args:
        file (str): URL or path to the CSV file.
    
    Returns:
        pandas.DataFrame: Processed DataFrame, or None if error.
    """
    try:
        df = pd.read_csv(file)
    except Exception as e:
        logger.error(f"Error reading CSV {file}: {e}")
        return None
    
    columns_to_keep = [
        'Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR',
        'B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA',
        'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA',
        'B365>2.5', 'B365<2.5', 'Max<2.5', 'Max>2.5',
        'Avg<2.5', 'Avg>2.5'
    ]
    
    missing_columns = [col for col in columns_to_keep if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing columns in {file}: {', '.join(missing_columns)}")
        return None
    
    df_selected = df[columns_to_keep].copy()
    
    # Drop NaN rows after filtering relevant columns
    df_selected = df_selected.dropna()
    
    # Add day of week
    try:
        df_selected['WeekDay'] = df_selected['Date'].apply(get_day_of_week)
    except ValueError as e:
        logger.error(f"Error processing dates in {file}: {e}")
        return None
    
    return df_selected

def add_FTRodds_feedback(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a column 'FTRodds_feedback' indicating if the favorite outcome (based on MaxH, MaxD, MaxA, AvgH, AvgD, AvgA)
    matches the actual outcome (FTR). Uses vectorized operations for performance.

    Args:
        df (pandas.DataFrame): Input DataFrame with 'FTR', 'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA' columns.

    Returns:
        pandas.DataFrame: DataFrame with new 'FTRodds_feedback' column ('True', 'False', or 'NA').

    Raises:
        ValueError: If required columns are missing.
    """
    try:
        # Validate input
        required_cols = ['FTR', 'MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA']
        if df is None or df.empty or not all(col in df.columns for col in required_cols):
            logger.warning("Invalid DataFrame or missing required columns for FTRodds_feedback")
            return df

        # Initialize output column
        df['FTRodds_feedback'] = 'NA'

        # Filter valid rows (non-NaN odds and valid FTR)
        valid = (~df[required_cols[1:]].isna().any(axis=1)) & (df['FTR'].isin(['H', 'A', 'D']))

        if valid.any():
            # Vectorized computation of minimum odds and favorites
            odds = df.loc[valid, ['MaxH', 'MaxD', 'MaxA', 'AvgH', 'AvgD', 'AvgA']]
            min_odds = odds.min(axis=1)
            
            # Determine favorite outcomes (columns where odds equal min_odds)
            favorites = odds.eq(min_odds, axis=0).apply(
                lambda x: [k[-1] for k in x.index[x] if k.startswith(('Max', 'Avg'))], axis=1
            )
            
            # Check if FTR is in favorites
            df.loc[valid, 'FTRodds_feedback'] = df.loc[valid, 'FTR'].combine(
                favorites, lambda ftr, fav: str(ftr in fav)
            )

        logger.info("Successfully added FTRodds_feedback column")
        return df

    except Exception as e:
        logger.error(f"Error in add_FTRodds_feedback: {str(e)}")
        raise

def add_Goalsodds_feedback(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a column 'Goalsodds_feedback' indicating if the favorite outcome for total goals (over/under 2.5, based on
    Max>2.5, Max<2.5, Avg>2.5, Avg<2.5) matches the actual total goals (FTHG + FTAG). Uses vectorized operations.

    Args:
        df (pandas.DataFrame): Input DataFrame with 'FTHG', 'FTAG', 'Max>2.5', 'Max<2.5', 'Avg>2.5', 'Avg<2.5' columns.

    Returns:
        pandas.DataFrame: DataFrame with new 'Goalsodds_feedback' column ('True', 'False', or 'NA').

    Raises:
        ValueError: If required columns are missing.
    """
    try:
        # Validate input
        required_cols = ['FTHG', 'FTAG', 'Max>2.5', 'Max<2.5', 'Avg>2.5', 'Avg<2.5']
        if df is None or df.empty or not all(col in df.columns for col in required_cols):
            logger.warning("Invalid DataFrame or missing required columns for Goalsodds_feedback")
            return df

        # Initialize output column
        df['Goalsodds_feedback'] = 'NA'

        # Filter valid rows (non-NaN goals and odds)
        valid = (~df[required_cols].isna().any(axis=1))

        if valid.any():
            # Calculate total goals and actual outcome
            total_goals = df.loc[valid, 'FTHG'] + df.loc[valid, 'FTAG']
            actual_outcome = np.where(total_goals > 2.5, 'Over', 'Under')

            # Vectorized computation of minimum odds and favorites
            odds = df.loc[valid, ['Max>2.5', 'Max<2.5', 'Avg>2.5', 'Avg<2.5']]
            min_odds = odds.min(axis=1)

            # Map odds columns to outcomes
            outcome_map = {'Max>2.5': 'Over', 'Avg>2.5': 'Over', 'Max<2.5': 'Under', 'Avg<2.5': 'Under'}
            favorites = odds.eq(min_odds, axis=0).apply(
                lambda x: [outcome_map[k] for k in x.index[x]], axis=1
            )

            # Check if actual outcome is in favorites
            df.loc[valid, 'Goalsodds_feedback'] = [
                str(outcome in favs) for outcome, favs in zip(actual_outcome, favorites)
            ]

        logger.info("Successfully added Goalsodds_feedback column")
        return df

    except Exception as e:
        logger.error(f"Error in add_Goalsodds_feedback: {str(e)}")
        raise

def add_total_goals_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a column 'TotalGoals' by summing FTHG and FTAG columns.

    Args:
        df (pandas.DataFrame): Input DataFrame with 'FTHG' and 'FTAG' columns.

    Returns:
        pandas.DataFrame: DataFrame with new 'TotalGoals' column (numeric or NaN).

    Raises:
        ValueError: If required columns are missing or contain non-numeric data.
    """
    try:
        # Validate input
        required_cols = ['FTHG', 'FTAG']
        if df is None or df.empty or not all(col in df.columns for col in required_cols):
            logger.warning("Invalid DataFrame or missing required columns for TotalGoals")
            return df

        # Check for numeric data
        if not all(df[col].dtype.kind in 'iuf' for col in required_cols):
            logger.error("FTHG and FTAG must be numeric")
            raise ValueError("FTHG and FTAG must be numeric")

        # Calculate total goals (vectorized)
        df['TotalGoals'] = df['FTHG'] + df['FTAG']

        # Set NaN for rows with missing FTHG or FTAG
        df.loc[df[required_cols].isna().any(axis=1), 'TotalGoals'] = np.nan

        logger.info("Successfully added TotalGoals column")
        return df

    except Exception as e:
        logger.error(f"Error in add_total_goals_column: {str(e)}")
        raise

def filter_club_games(var_club_name, df):
    """
    Filter games for a specific club (home or away).
    
    Args:
        var_club_name (str): Name of the club.
        df (pandas.DataFrame): Input DataFrame.
    
    Returns:
        pandas.DataFrame: Filtered DataFrame, or None if error.
    """
    if df is None or df.empty:
        return None
    return df.loc[(df['HomeTeam'] == var_club_name) | (df['AwayTeam'] == var_club_name)].copy()

def filter_clubs_names(file="https://www.football-data.co.uk/mmz4281/2324/I1.csv"):
    """
    Print unique club names from a CSV file.
    
    Args:
        file (str): URL or path to the CSV file.
    """
    try:
        df = pd.read_csv(file)
        club_names = df['HomeTeam'].unique()
        for name in sorted(club_names):
            logger.info(name)
    except Exception as e:
        logger.error(f"Error reading club names from {file}: {e}")

def finalscore_and_teams(df):
    """
    Extract teams and final scores from a DataFrame.
    
    Args:
        df (pandas.DataFrame): Input DataFrame.
    
    Returns:
        pandas.DataFrame: DataFrame with teams and scores.
    """
    if df is None or df.empty:
        return None
    selected_columns = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
    return df[selected_columns].copy()

def data_treatmentP(file):
    """
    Process a CSV file by removing unnecessary columns.
    
    Args:
        file (str): URL or path to the CSV file.
    
    Returns:
        pandas.DataFrame: Processed DataFrame, or None if error.
    """
    try:
        df = pd.read_csv(file)
    except Exception as e:
        logger.error(f"Error reading CSV {file}: {e}")
        return None
    
    columns_to_remove = [
        'Div', 'FTR', 'HTAG', 'HTR', 'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 'HY', 'AY',
        'HR', 'AR', 'IWH', 'IWD', 'IWA', 'PSH', 'PSD', 'PSA', 'WHH', 'WHD', 'WHA', 'VCH', 'VCD', 'VCA',
        'B365AHH', 'B365AHA', 'PAHH', 'PAHA', 'MaxAHH', 'MaxAHA', 'AvgAHH', 'AvgAHA', 'B365CH', 'B365CD',
        'B365CA', 'BWCH', 'BWCD', 'BWCA', 'IWCH', 'IWCD', 'IWCA', 'PSCH', 'PSCD', 'PSCA', 'WHCH', 'WHCD',
        'WHCA', 'VCCH', 'VCCD', 'VCCA'
    ]
    
    missing_columns = [col for col in columns_to_remove if col not in df.columns]
    if missing_columns:
        logger.warning(f"Columns not found in DataFrame: {', '.join(missing_columns)}")
    
    df = df.drop(columns=[col for col in columns_to_remove if col in df.columns], errors='ignore')
    df = df.dropna()
    
    return df

def get_date(df_team):
    """
    Extract dates from a DataFrame.
    
    Args:
        df_team (pandas.DataFrame): Input DataFrame.
    
    Returns:
        pandas.Series: Series of dates.
    """
    if df_team is None or 'Date' not in df_team.columns:
        return None
    return df_team['Date']

def treatment_of_date(df):
    """
    Convert dates and extract day, month, and day of week.
    
    Args:
        df (pandas.DataFrame): Input DataFrame.
    
    Returns:
        pandas.DataFrame: Processed DataFrame.
    """
    if df is None or 'Date' not in df.columns:
        return df
    
    # Try multiple date formats
    date_formats = ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d']
    for fmt in date_formats:
        try:
            df['Date'] = pd.to_datetime(df['Date'], format=fmt, dayfirst=True)
            break
        except ValueError:
            continue
    else:
        logger.warning("Could not parse dates")
        return df
    
    df['Day'] = df['Date'].dt.day
    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    df['Day_of_week'] = df['Date'].dt.dayofweek
    df = df.drop(columns=['Date'])
    
    return df

def get_day_of_week(date_str):
    """
    Get the day of the week (0=Mon, 6=Sun) from a date string.
    
    Args:
        date_str (str): Date string.
    
    Returns:
        int: Day of the week number.
    """
    try:
        date_formats = ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d']
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.weekday()
            except ValueError:
                continue
        return None
    except Exception as e:
        logger.error(f"Error parsing date {date_str}: {e}")
        return None

def replace_club_names_with_indices(df, star_club, opp_club):
    """
    Replace club names with indices (99 for star_club, 98 for opp_club, others from url.clubs_by_league).
    
    Args:
        df (pandas.DataFrame): Input DataFrame.
        star_club (str): Main club.
        opp_club (str): Opponent club.
    
    Returns:
        pandas.DataFrame: DataFrame with indices.
    """
    if df is None or df.empty:
        return df
    
    reverse_clubs = {}
    for league, clubs in url.clubs_by_league.items():
        for idx, club in enumerate(clubs, start=1):
            reverse_clubs[club] = idx
    
    def map_club(club):
        if club == star_club:
            return 99.0
        elif club == opp_club:
            return 98.0
        return reverse_clubs.get(club, 0.0)  # Default to 0.0 for unknown clubs
    
    df['HomeTeam'] = df['HomeTeam'].apply(map_club)
    df['AwayTeam'] = df['AwayTeam'].apply(map_club)
    
    return df

def replace_ftr(df, selected_team, encoding='binary'):
    """
    Replace FTR column based on selected team outcomes.
    
    Args:
        df (pandas.DataFrame): Input DataFrame.
        selected_team (str): Selected team.
        encoding (str): 'binary' (1=win, 0=other) or 'ternary' (1=win, 0=draw, 2=loss).
    
    Returns:
        pandas.DataFrame: DataFrame with modified FTR.
    """
    if df is None or df.empty or 'FTR' not in df.columns:
        return df
    
    if encoding == 'binary':
        df['FTR'] = df.apply(
            lambda row: 1 if (row['FTR'] == 'H' and row['HomeTeam'] == selected_team) or
                             (row['FTR'] == 'A' and row['AwayTeam'] == selected_team) else 0,
            axis=1
        )
    elif encoding == 'ternary':
        df['FTR'] = df.apply(
            lambda row: 1 if (row['FTR'] == 'H' and row['HomeTeam'] == selected_team) or
                             (row['FTR'] == 'A' and row['AwayTeam'] == selected_team) else
                        (2 if (row['FTR'] == 'H' and row['AwayTeam'] == selected_team) or
                              (row['FTR'] == 'A' and row['HomeTeam'] == selected_team) else 0),
            axis=1
        )
    return df