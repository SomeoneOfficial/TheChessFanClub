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
save_path = os.path.join("Fetch", "Fetch.json")
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/x-ndjson"
}

def load_cached_data():
    """Loads existing tournament data from JSON to resume progress."""
    if os.path.exists(save_path):
        try:
            with open(save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "tournaments" in data and "player_leaderboard" in data:
                    print(f"🔄 Resuming from existing cache ({len(data['tournaments'])} tournaments loaded).")
                    return data
        except Exception as e:
            print(f"⚠️ Failed to parse existing JSON cache ({e}). Starting fresh.")
    return {"tournaments": {}, "player_leaderboard": {}}

def get_team_battles(team_slug):
    arena_url = f"https://lichess.org/api/team/{team_slug}/arena"
    print(f"Connecting to: {arena_url}")
    tournaments = []
    
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
    
    # Load previous cache state
    cache = load_cached_data()
    cached_tournaments = cache["tournaments"]
    
    all_battles = get_team_battles(team_id)
    
    if not all_battles:
        print("No team battle arenas found to analyze.")
    else:
        # Filter 1: Only include finished tournaments (status 30 and no secondsToStart)
        valid_battles = [
            b for b in all_battles 
            if b.get("status") == 30 and "secondsToStart" not in b
        ]
        
        # Filter 2: Skip tournaments already fetched in our JSON file
        battles_to_fetch = {
            b.get("id"): b for b in valid_battles 
            if b.get("id") and b.get("id") not in cached_tournaments
        }
        
        print(f"📋 Total finished tournaments found: {len(valid_battles)}")
        print(f"⚡ {len(battles_to_fetch)} new tournaments require fetching.")
        
        if battles_to_fetch:
            with requests.Session() as session:
                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = {
                        executor.submit(fetch_tournament_data, session, b_id): b_id 
                        for b_id in battles_to_fetch
                    }
                    
                    for future in as_completed(futures):
                        b_id, lines = future.result()
                        battle_info = battles_to_fetch.get(b_id)
                        b_name = battle_info.get("fullName", b_id)
                        
                        if lines is None:
                            print(f"❌ Skipping {b_name} ({b_id}) due to HTTP error.")
                            continue
                            
                        print(f"✅ Processing: {b_name} ({b_id})")
                        
                        # Store metadata
                        date_finished = battle_info.get("startsAt", "Unknown Date")
                        cached_tournaments[b_id] = {
                            "fullName": b_name,
                            "date": date_finished
                        }
                        
                        # Tally player scores into the cache database
                        for player_data in lines:
                            if player_data.get("team") == team_id:
                                username = player_data.get("username")
                                points = player_data.get("score", 0)
                                
                                current_score = cache["player_leaderboard"].get(username, 0)
                                cache["player_leaderboard"][username] = current_score + points

        # Sort leaderboard based on accumulated history plus new changes (sorted by points descending)
        sorted_leaderboard = sorted(
            cache["player_leaderboard"].items(), 
            key=lambda item: item[1], 
            reverse=True
        )
        
        # Display Leaderboard
        print("\n" + "=" * 50)
        print("🏆 FINAL CUMULATIVE TEAM LEADERBOARD 🏆")
        print("=" * 50)
        for rank, (player, total_score) in enumerate(sorted_leaderboard, 1):
            print(f"{rank:02d}. {player:<25} Total Points: {total_score}")

        # Update configuration dictionary to hold the sorted dictionary format
        cache["player_leaderboard"] = dict(sorted_leaderboard)
        
        # Save updated database state to file
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=4)
            
        print(f"\n📁 Database updated and successfully saved to: {save_path}")
