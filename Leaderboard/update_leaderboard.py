import os
import json
import requests
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# 1. Setup Environment
load_dotenv(".env")
token = os.getenv("LICHESS_TOKEN")
team_id = "the-chess-fan-club"

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/x-ndjson"
}

def get_team_battles(team_slug):
    arena_url = f"https://lichess.org/api/team/{team_slug}/arena"
    print(f"Connecting to: {arena_url}")
    tournaments = []
    
    # Use a persistent session for better connection pooling
    with requests.Session() as session:
        response = session.get(arena_url, headers=headers, stream=True)
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    tournaments.append(json.loads(line.decode('utf-8')))
        else:
            print(f"Failed to fetch team arenas. HTTP {response.status_code}")
    return tournaments

def fetch_tournament_data(session, tournament_id):
    """Worker function to strictly fetch data from Lichess API."""
    clean_id = str(tournament_id).strip("/").split("/")[-1]
    results_url = f"https://lichess.org/api/tournament/{clean_id}/results"
    
    try:
        response = session.get(results_url, headers=headers, stream=True)
        if response.status_code != 200:
            return clean_id, None
            
        lines = []
        for line in response.iter_lines():
            if line:
                lines.append(json.loads(line.decode('utf-8')))
        return clean_id, lines
    except Exception:
        return clean_id, None

if __name__ == "__main__":
    print(f"Starting leaderboard accumulation for team: {team_id}...")
    all_battles = get_team_battles(team_id)
    
    if not all_battles:
        print("No team battle arenas found to analyze.")
    else:
        master_leaderboard = defaultdict(int)
        
        # Create a dictionary to map IDs to full names for quick lookups
        battle_names = {b.get("id"): b.get("fullName") for b in all_battles if b.get("id")}
        
        # Use ThreadPoolExecutor to request tournaments in parallel
        # Max 10 workers to keep within polite API limits and prevent rate limiting
        print(f"\n⚡ Fetching data for {len(battle_names)} tournaments concurrently...")
        
        with requests.Session() as session:
            with ThreadPoolExecutor(max_workers=2) as executor:
                # Submit all download tasks to the thread pool
                futures = {
                    executor.submit(fetch_tournament_data, session, b_id): b_id 
                    for b_id in battle_names
                }
                
                # Process results as soon as each individual download finishes
                for future in as_completed(futures):
                    b_id, lines = future.result()
                    b_name = battle_names.get(b_id)
                    
                    if lines is None:
                        print(f"❌ Skipping {b_name} ({b_id}) due to connection failure or HTTP error.")
                        continue
                        
                    print(f"✅ Processing: {b_name} ({b_id})")
                    battle_points_tallied = 0
                    
                    for player_data in lines:
                        if player_data.get("team") == team_id:
                            username = player_data.get("username")
                            points = player_data.get("score", 0)
                            master_leaderboard[username] += points
                            battle_points_tallied += points
                            
                    print(f"   Total points contributed this battle: {battle_points_tallied}")

        print("\n" + "=" * 50)
        print("🏆 FINAL CUMULATIVE TEAM LEADERBOARD 🏆")
        print("=" * 50)
        
        sorted_leaderboard = sorted(master_leaderboard.items(), key=lambda item: item[1], reverse=True)
        
        for rank, (player, total_score) in enumerate(sorted_leaderboard, 1):
            print(f"{rank:02d}. {player:<25} Total Points: {total_score}")
