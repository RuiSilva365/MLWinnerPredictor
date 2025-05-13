#!/usr/bin/env python3
# test_python_api.py
# This script tests the Python API directly, bypassing the Go API

import requests
import json
import time
import sys
import os
import urllib.parse
import nextGameScrapping

def test_python_api():
    """
    Test the Python API directly
    """
    # Python API base URL
    base_url = "http://localhost:5000/api"
    
    print("Testing the Python API directly...")
    
    # Check if the Python server is running
    try:
        response = requests.get(f"{base_url}/leagues", timeout=5)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the Python API server at http://localhost:5000")
        print("Make sure the server is running using ./start_servers.sh")
        return False
    
    # 1. Get available leagues
    print("\n1. Getting available leagues...")
    try:
        response = requests.get(f"{base_url}/leagues")
        if response.status_code == 200:
            leagues = response.json().get('leagues', [])
            print(f"  Available leagues: {', '.join(leagues) if leagues else 'None'}")
        else:
            print(f"  Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  Request error: {str(e)}")
        return False
    
    if not leagues:
        print("  No leagues available. Check that the API is properly connected to the league data.")
        return False
    
    # Find Serie A in the list of leagues
    selected_league = str(input("Insert a league: "))
    if selected_league not in leagues:
        selected_league = leagues[0]  # Use the first league as fallback
        print(f"  La Liga not found in leagues, using {selected_league} instead")
    
    # 2. Get teams for a league
    print(f"\n2. Getting teams for {selected_league}...")
    # Properly encode the league parameter
    encoded_league = urllib.parse.quote(selected_league)
    
    try:
        response = requests.get(f"{base_url}/teams?league={encoded_league}")
        if response.status_code == 200:
            teams = response.json().get('teams', [])
            print(f"  Available teams: {', '.join(teams[:5])}... (and {len(teams)-5} more)" if len(teams) > 5 else f"  Available teams: {', '.join(teams)}")
        else:
            print(f"  Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  Request error: {str(e)}")
        return False
    
    if len(teams) < 2:
        print("  Not enough teams available. Check the league data.")
        return False
    
    # Try to find Atalanta and Roma in the list of teams
    team1 =str(input("Insert the home Team: "))
    team2 =str(input("Insert the away Team: "))
    
    if team1 not in teams:
        team1 = teams[0]  # Use first team as fallback
        print(f"  {team1} not found in teams, using {teams[0]} instead")
    
    if team2 not in teams:
        team2 = teams[1]  # Use second team as fallback
        print(f"  {team2} not found in teams, using {teams[1]} instead")
    
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
    max_attempts = 20  # Increased number of attempts
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
        response = requests.get(f"{base_url}/data/team?team=team1")
        if response.status_code == 200:
            data_response = response.json()
            shape = data_response.get('shape', [0, 0])
            columns = data_response.get('columns', [])
            print(f"  DataFrame shape: {shape[0]} rows x {shape[1]} columns")
            print(f"  Columns: {', '.join(columns[:5])}... (and {len(columns)-5} more)" if len(columns) > 5 else f"  Columns: {', '.join(columns)}")
        else:
            print(f"  Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  Request error: {str(e)}")
        return False
    
    # 6. Get next game data
    print("\n6. Getting next game data...")
    try:
        odds_data = nextGameScrapping.get_next_game_data('', team1, team2, '',selected_league)
        goals_data = nextGameScrapping.get_next_game_goals_data('', team1, team2, '',selected_league)


        response = requests.get(f"{base_url}/data/next-game")
        if response.status_code == 200:
            data_response = response.json()
            data = data_response.get('data', [])
            if data:
                print(f"  Next game: {data[0].get('HomeTeam')} vs {data[0].get('AwayTeam')}")
                print(f"  Odds Home: {data[0].get('B365H')}, Draw: {data[0].get('B365D')}, Away: {data[0].get('B365A')}")
            else:
                print("  No next game data available.")
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