# main.py
# Main script for processing football data and generating league table with user input
import pandas as pd
import treatment
import url
import league_table
import weather
import nextGame
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('main.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def get_user_input() -> dict:
    """Prompt user for league, clubs, season, and game date with validation."""
    print("Available leagues:", ", ".join(url.available_leagues))
    league = input("Enter the league (e.g., Serie A): ").strip()
    if league not in url.available_leagues:
        logger.error(f"Invalid league: {league}")
        raise ValueError(f"League '{league}' is not supported. Choose from {url.available_leagues}")
    
    print(f"Available clubs for {league}:", ", ".join(url.clubs_by_league[league]))
    star_club = input(f"Enter the main club for {league}: ").strip()
    if star_club not in url.clubs_by_league[league]:
        logger.error(f"Invalid club: {star_club}")
        raise ValueError(f"Club '{star_club}' is not in {league}. Choose from {url.clubs_by_league[league]}")
    
    opp_club = input(f"Enter the opponent club for {league}: ").strip()
    if opp_club not in url.clubs_by_league[league]:
        logger.error(f"Invalid club: {opp_club}")
        raise ValueError(f"Club '{opp_club}' is not in {league}. Choose from {url.clubs_by_league[league]}")
    
    season_input = input("Enter the latest season start year (e.g., 2024 for 2024/2025, default 2024): ").strip()
    try:
        season = int(season_input) if season_input else 2024
        if season < 2020 or season > 2024:
            logger.error(f"Invalid season: {season}")
            raise ValueError("Season must be between 2020 and 2024")
    except ValueError as e:
        logger.error(f"Invalid season input: {season_input}")
        raise ValueError("Season must be a valid year (e.g., 2024)") from e
    
    current_date = datetime.now().strftime('%d/%m/%Y')
    game_date = input(f"Enter the next game date (DD/MM/YYYY, default {current_date}): ").strip()
    if not game_date:
        game_date = current_date
    try:
        datetime.strptime(game_date, '%d/%m/%Y')
    except ValueError:
        logger.error(f"Invalid date format: {game_date}")
        raise ValueError("Game date must be in DD/MM/YYYY format (e.g., 17/05/2025)")
    
    return {
        "league": league,
        "star_club": star_club,
        "opp_club": opp_club,
        "season": season,
        "game_date": game_date
    }

def main():
    """Main function to process football data and generate outputs."""
    try:
        # Get user input
        inputs = get_user_input()
        league = inputs["league"]
        star_club = inputs["star_club"]
        opp_club = inputs["opp_club"]
        season = inputs["season"]
        game_date = inputs["game_date"]
        
        print(f"Processing data for {league} season {season}/{season + 1}...")
        print(f"Clubs: {star_club} vs {opp_club}")
        error = treatment.handler(season, league, star_club, opp_club)
        if error:
            print(f"Error processing data: {error}")
            logger.error(f"Error processing data: {error}")
            return
        
        if not os.path.exists("AllGames.csv"):
            print("Error: AllGames.csv not found. Cannot proceed.")
            logger.error("AllGames.csv not found")
            return
        
        print("Building league table with position information...")
        league_table.update_all_dataframes_with_positions(league)
        
        # Load team and opponent games
        if not os.path.exists("TeamGames.csv") or not os.path.exists("OppGames.csv"):
            print("Error: TeamGames.csv or OppGames.csv not found.")
            logger.error("TeamGames.csv or OppGames.csv not found")
            return
        
        team_games = pd.read_csv("TeamGames.csv")
        opp_games = pd.read_csv("OppGames.csv")
        
        # Add columns
        print("Adding TotalGoals column...")
        team_games = treatment.add_total_goals_column(team_games)
        opp_games = treatment.add_total_goals_column(opp_games)
        
        print("Adding FTR odds feedback columns...")
        team_games = treatment.add_FTRodds_feedback(team_games)
        opp_games = treatment.add_FTRodds_feedback(opp_games)
        
        print("Adding goals odds feedback columns...")
        team_games = treatment.add_Goalsodds_feedback(team_games)
        opp_games = treatment.add_Goalsodds_feedback(opp_games)
        
        print("Processing dates...")
        team_games = treatment.treatment_of_date(team_games)
        opp_games = treatment.treatment_of_date(opp_games)
        
        # Add weather data before saving treated files
        print("Adding weather data...")
        team_games = weather.enrich_with_weather(team_games, league)
        opp_games = weather.enrich_with_weather(opp_games, league)
        
        print("Saving treated files...")
        team_games.to_csv("TeamGamesTreated.csv", index=False)
        opp_games.to_csv("OppGamesTreated.csv", index=False)
        logger.info("Saved TeamGamesTreated.csv and OppGamesTreated.csv")
        
        # Combine treated files
        print("Combining treated files...")
        for col in ['Day', 'Month', 'Year']:
            team_games[col] = pd.to_numeric(team_games[col], errors='coerce').fillna(0).astype(int)
            opp_games[col] = pd.to_numeric(opp_games[col], errors='coerce').fillna(0).astype(int)
            logger.info(f"Column {col} types - TeamGames: {team_games[col].dtype}, OppGames: {opp_games[col].dtype}")
        
        combined_df = pd.concat([team_games, opp_games]).drop_duplicates(
            subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'Day', 'Month', 'Year']
        )
        combined_df = weather.enrich_with_weather(combined_df, league)
        combined_df.to_csv("CombinedGamesTreated.csv", index=False)
        logger.info(f"Saved CombinedGamesTreated.csv with {len(combined_df)} rows")
        
        # Generate NextGame.csv using nextGame.py
        print("Generating/Updating NextGame.csv...")
        try:
            nextGame.create_next_game(star_club, opp_club, league, game_date, season)
            logger.info("Generated NextGame.csv via nextGame.py")
            
            # Add weather data to NextGame.csv
            if os.path.exists("NextGame.csv"):
                next_game_df = pd.read_csv("NextGame.csv")
                next_game_df = weather.enrich_with_weather(next_game_df, league)
                if next_game_df[['Temperature', 'Precipitation', 'WeatherCode']].notna().any().any():
                    next_game_df.to_csv("NextGame.csv", index=False)
                    logger.info("Added weather data to NextGame.csv")
                else:
                    logger.warning("Weather data not applied to NextGame.csv")
            
            # Update NextGame.csv with latest team positions
            print("Updating NextGame.csv with latest team positions...")
            league_table.update_next_game_with_latest_positions(league)
        except Exception as e:
            logger.error(f"Failed to generate/update NextGame.csv: {e}")
            print(f"Warning: Could not generate NextGame.csv: {e}")
        
        # Display results
        if os.path.exists("NextGame.csv"):
            next_game_df = pd.read_csv("NextGame.csv")
            if not next_game_df.empty:
                home_team = next_game_df.iloc[0]['HomeTeam']
                away_team = next_game_df.iloc[0]['AwayTeam']
                home_pos = next_game_df.iloc[0].get('HomePosition', 'Unknown')
                away_pos = next_game_df.iloc[0].get('AwayPosition', 'Unknown')
                print(f"NextGame positions: {home_team}={home_pos}, {away_team}={away_pos}")
        
        print(f"\nLeague Table for Season {season}/{season + 1}:")
        table_df = league_table.get_current_league_table(league, season)
        
        if not table_df.empty:
            star_club_row = table_df[table_df['Team'] == star_club]
            opp_club_row = table_df[table_df['Team'] == opp_club]
            
            star_pos = star_club_row['Position'].iloc[0] if not star_club_row.empty else "Unknown"
            opp_pos = opp_club_row['Position'].iloc[0] if not opp_club_row.empty else "Unknown"
            
            print(f"Current position of {star_club}: {star_pos}")
            print(f"Current position of {opp_club}: {opp_pos}")
            
            max_pos = max(
                star_club_row['Position'].iloc[0] if not star_club_row.empty else 10,
                opp_club_row['Position'].iloc[0] if not opp_club_row.empty else 10,
                10
            )
            print(f"\nTop {max_pos} Teams:")
            print(table_df.head(max_pos)[['Position', 'Team', 'Played', 'Won', 'Drawn', 'Lost', 'Points']])
        else:
            print("Could not generate league table - insufficient data")
            logger.error("Failed to generate league table")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        logger.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()