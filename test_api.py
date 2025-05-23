#!/usr/bin/env python3
# test_python_api.py
# This script tests the Python API directly, bypassing the Go API

import requests
import json
import time
import sys
import os
import urllib.parse
import nextGame
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def test_python_api():
    """
    Test the Python API directly
    """
    # Python API base URL
    base_url = "http://192.168.1.130:8080"
    
    print("Testing the Python API directly...")
    
    # Check if the Python server is running
    try:
        response = requests.get(f"{base_url}/leagues", timeout=5)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the Python API server at http://192.168.1.130:8080")
        print("Make sure the server is running using ./start_servers.sh")
        return False
    
    # 1. Get available leagues
    print("\n1. Getting available leagues...")
    try:
        response = requests.get(f"{base_url}/leagues")
        if response.status_code == 200:
            leagues = response.json().get('leagues', [])
            if leagues:
                print("  Available leagues:")
                for i, league in enumerate(leagues, 1):
                    print(f"    {i}. {league}")
            else:
                print("  No leagues available")
        else:
            print(f"  Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  Request error: {str(e)}")
        return False
    
    if not leagues:
        print("  No leagues available. Check that the API is properly connected to the league data.")
        return False
    
    # Get league selection
    selected_league = input("Insert a league name or number: ").strip()
    try:
        league_idx = int(selected_league) - 1
        if 0 <= league_idx < len(leagues):
            selected_league = leagues[league_idx]
        else:
            print(f"  Invalid league number, checking if '{selected_league}' is a valid league name")
            if selected_league not in leagues:
                selected_league = leagues[0]
                print(f"  '{selected_league}' not found, using {leagues[0]} instead")
    except ValueError:
        if selected_league not in leagues:
            selected_league = leagues[0]
            print(f"  '{selected_league}' not found, using {leagues[0]} instead")
    
    # 2. Get teams for a league
    print(f"\n2. Getting teams for {selected_league}...")
    encoded_league = urllib.parse.quote(selected_league)
    
    try:
        response = requests.get(f"{base_url}/teams?league={encoded_league}")
        if response.status_code == 200:
            teams = response.json().get('teams', [])
            if teams:
                print("  Available teams:")
                for i, team in enumerate(teams, 1):
                    print(f"    {i}. {team}")
            else:
                print("  No teams available")
        else:
            print(f"  Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  Request error: {str(e)}")
        return False
    
    if len(teams) < 2:
        print("  Not enough teams available. Check the league data.")
        return False
    
    # Function to get team selection by name or index
    def get_team_selection(prompt, teams):
        while True:
            selection = input(prompt).strip()
            try:
                idx = int(selection) - 1
                if 0 <= idx < len(teams):
                    return teams[idx]
                print(f"  Invalid team number. Please enter a number between 1 and {len(teams)}")
            except ValueError:
                if selection in teams:
                    return selection
                print(f"  Team '{selection}' not found. Please enter a valid team name or number.")
    
    # Get team selections
    team1 = get_team_selection("Insert the home team (name or number): ", teams)
    team2 = get_team_selection("Insert the away team (name or number): ", teams)
    
    # Ensure different teams
    while team1 == team2:
        print("  Home and away teams cannot be the same!")
        team2 = get_team_selection("Insert the away team (name or number): ", teams)
    
    # 3. Start a data processing job
    print(f"\n3. Starting data processing for {team1} vs {team2}...")
    
    prediction_request = {
        "season": 2020,
        "league": selected_league,
        "team1": team1,
        "team2": team2,
        "gameDate": "12/05/2025"
    }
    
    try:
        response = requests.post(f"{base_url}/predict", json=prediction_request)
        if response.status_code == 200:
            job_response = response.json()
            job_id = job_response.get('job_id')
            print(f"  Job started with ID: {job_id}")
            print(f"  Status: {job_response.get('status')}")
        else:
            print(f"  Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  Request error: {str(e)}")
        return False
    
    if not job_id:
        print("  Failed to get job ID. Check the API response.")
        return False
    
    # 4. Check job status until completed or error
    print("\n4. Checking job status...")
    max_attempts = 20
    attempt = 0
    status = "pending"
    
    while status in ["pending", "processing"] and attempt < max_attempts:
        attempt += 1
        print(f"  Attempt {attempt}/{max_attempts}...")
        
        try:
            response = requests.get(f"{base_url}/jobs/{job_id}")
            if response.status_code == 200:
                job_status = response.json()
                status = job_status.get('status')
                print(f"  Status: {status}")
                
                if status == "completed":
                    result = job_status.get('result', {})
                    print(f"  Team1 ({result.get('team1', {}).get('name')}): {result.get('team1', {}).get('games_count')} games")
                    print(f"  Team2 ({result.get('team2', {}).get('name')}): {result.get('team2', {}).get('games_count')} games")
                    print("  Next game odds available:", "Yes" if result.get('next_game', {}).get('odds') else "No")
                elif status == "error":
                    print(f"  Error: {job_status.get('error')}")
                    return False
            else:
                print(f"  Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"  Request error: {str(e)}")
            return False
        
        if status in ["pending", "processing"]:
            print("  Waiting 5 seconds before next check...")
            time.sleep(5)
    
    if status != "completed":
        print("  Job did not complete successfully. Check the API logs.")
        return False
    
    # 5. Get team data
    print("\n5. Getting team1 data...")
    try:
        response = requests.get(f"{base_url}/data/team?team={urllib.parse.quote(team1)}")
        if response.status_code == 200:
            data_response = response.json()
            shape = data_response.get('shape', [0, 0])
            columns = data_response.get('columns', [])
            print(f"  DataFrame shape: {shape[0]} rows x {shape[1]} columns")
            print(f"  Columns: {', '.join(columns)}")
        else:
            print(f"  Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  Request error: {str(e)}")
        return False
    
    # 6. Get next game data
    print("\n6. Getting next game data...")
    try:
        # Fetch odds and goals data using NextGameScraper
        odds_data = nextGame.get_next_game_data('', team1, team2, '12/05/2025', selected_league)
        goals_data = nextGame.get_next_game_goals_data('', team1, team2, '12/05/2025', selected_league)

        # Check if odds data contains an error
        if 'error' in odds_data:
            print(f"  Error retrieving odds: {odds_data['error']}")
        else:
            print(f"  Odds retrieved: Home: {odds_data.get('B365H', 'N/A')}, "
                  f"Draw: {odds_data.get('B365D', 'N/A')}, Away: {odds_data.get('B365A', 'N/A')}")

        # Check if goals data contains an error
        if 'error' in goals_data:
            print(f"  Error retrieving goals odds: {goals_data['error']}")
        else:
            print(f"  Goals odds retrieved: Over 2.5: {goals_data.get('B365>2.5', 'N/A')}, "
                  f"Under 2.5: {goals_data.get('B365<2.5', 'N/A')}")

        # Try to get next game data from the API
        response = requests.get(f"{base_url}/data/next-game")
        if response.status_code == 200:
            data_response = response.json()
            data = data_response.get('data', [])
            if data:
                print(f"  Next game: {data[0].get('HomeTeam')} vs {data[0].get('AwayTeam')}")
                print(f"  Odds Home: {data[0].get('B365H', 'N/A')}, "
                      f"Draw: {data[0].get('B365D', 'N/A')}, Away: {data[0].get('B365A', 'N/A')}")
            else:
                print("  No next game data available from API.")
        else:
            print(f"  Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  Request error: {str(e)}")
        return False
    
    print("\nAll tests to the Python API completed successfully!")
    print("If this test passes but the original test fails, the issue is with the Go API.")
    return True

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)  # Change to the script's directory
    
    success = test_python_api()
    sys.exit(0 if success else 1)