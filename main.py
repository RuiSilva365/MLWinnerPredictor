import pandas as pd
import treatment
import nextGameScrapping
import url
import prediction

def main():
    # Test parameters
    season = 2020  # Start from 2020/2021
    league = "Serie A"
    star_club = "Atalanta"
    opp_club = "Roma"
    odds_url = "https://www.oddsportal.com/football/italy/serie-a/atalanta-as-roma-KfCgL6Wp/#1X2;2"
    game_date = "12/05/2025"  # Hypothetical future game date
    
    # Process historical data
    print(f"Processing historical data for {star_club} vs {opp_club} in {league}...")
    error = treatment.handler(season, league, star_club, opp_club)
    if error:
        print(error)
        return
    
    # Load processed data
    team_games = pd.read_csv("TeamGames.csv")
    opp_games = pd.read_csv("OppGames.csv")
    
    # Replace club names with indices
    print(f"Replacing club names with indices for {star_club} and {opp_club}...")
    #team_games = treatment.replace_club_names_with_indices(team_games, star_club, opp_club)
    #opp_games = treatment.replace_club_names_with_indices(opp_games, star_club, opp_club)
    
    # Add total goals column
    print("Adding TotalGoals column...")
    team_games = treatment.add_total_goals_column(team_games)
    opp_games = treatment.add_total_goals_column(opp_games)
    
    # Add FTR odds feedback
    print("Adding FTR odds feedback columns...")
    team_games = treatment.add_FTRodds_feedback(team_games)
    opp_games = treatment.add_FTRodds_feedback(opp_games)
    
    # Add goals odds feedback
    print("Adding goals odds feedback columns...")
    team_games = treatment.add_Goalsodds_feedback(team_games)
    opp_games = treatment.add_Goalsodds_feedback(opp_games)
    
    # Process dates
    print("Processing dates...")
    team_games = treatment.treatment_of_date(team_games)
    opp_games = treatment.treatment_of_date(opp_games)
    
    # Drop Date column if it exists
    print("Dropping Date column if it exists...")
    if 'Date' in team_games.columns:
        team_games = team_games.drop('Date', axis=1)
    if 'Date' in opp_games.columns:
        opp_games = opp_games.drop('Date', axis=1)
    

        # Drop WeekDay column if it exists
    print("Dropping Date column if it exists...")
    if 'WeekDay' in team_games.columns:
        team_games = team_games.drop('WeekDay', axis=1)
    if 'WeekDay' in opp_games.columns:
        opp_games = opp_games.drop('WeekDay', axis=1)
    
    # Save treated data
    print("Saving treated files: TeamGamesTreated.csv, OppGamesTreated.csv")
    team_games.to_csv("TeamGamesTreated.csv", index=False)
    opp_games.to_csv("OppGamesTreated.csv", index=False)
    
    # Fetch odds for upcoming game
    print(f"Fetching odds for upcoming game: {odds_url}")
    odds_data = nextGameScrapping.get_next_game_data(odds_url, star_club, opp_club, game_date, league)
    goals_data = nextGameScrapping.get_next_game_goals_data(odds_url, star_club, opp_club, game_date, league)
    print(f"1X2 Odds: {odds_data}")
    print(f"Goals Odds: {goals_data}")

    prediction_df = pd.read_csv("NextGame.csv")



    prediction_results = prediction.predict(
            train_df=team_games, 
            test_df=opp_games, 
            pred_df=prediction_df
        )
    print("Prediction results:")    

if __name__ == "__main__":
    main()