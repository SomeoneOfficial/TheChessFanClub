import requests
import json
import time
import random
import re

from collections import defaultdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


TEAM_ID = "the-chess-fan-club"

HEADERS = {
    "Accept": "application/x-ndjson",
    "User-Agent": "ChessFanClubLeaderboard/1.0"
}


leaderboard = defaultdict(lambda: {
    "points": 0,
    "tournaments": 0,
    "wins": 0
})


# ----------------------------------
# GET CURRENT TEAM MEMBERS
# ----------------------------------

def get_team_members():

    print("Fetching current team members...")

    url = (
        "https://lichess.org/team/"
        "the-chess-fan-club/members"
    )


    r = requests.get(
        url,
        headers={
            "User-Agent": "ChessFanClubLeaderboard/1.0"
        },
        timeout=30
    )

    r.raise_for_status()


    members = set()


    usernames = re.findall(
        r'/@/([^"\s?]+)',
        r.text
    )


    for username in usernames:

        members.add(
            username.lower()
        )


    return members



# ----------------------------------
# GET TEAM TOURNAMENTS
# ----------------------------------

def get_team_tournaments():

    print("Fetching tournaments...")


    url = (
        f"https://lichess.org/api/team/"
        f"{TEAM_ID}/arena"
    )


    tournaments = []


    with requests.get(
        url,
        headers=HEADERS,
        stream=True,
        timeout=30
    ) as r:


        r.raise_for_status()


        for line in r.iter_lines():

            if line:

                tournaments.append(
                    json.loads(line)
                )


    return tournaments




# ----------------------------------
# GET TOURNAMENT RESULTS
# ----------------------------------

def get_tournament_results(tournament):


    tournament_id = tournament["id"]


    url = (
        f"https://lichess.org/api/"
        f"tournament/{tournament_id}"
        f"/results?nb=1000"
    )


    players = []


    for attempt in range(5):

        try:

            r = requests.get(
                url,
                headers=HEADERS,
                stream=True,
                timeout=60
            )


            if r.status_code == 429:

                wait = (attempt + 1) * 10

                print(
                    "Rate limited. Waiting",
                    wait,
                    "seconds"
                )

                time.sleep(wait)

                continue


            r.raise_for_status()


            for line in r.iter_lines():

                if line:

                    players.append(
                        json.loads(line)
                    )


            break



        except Exception as e:


            if attempt == 4:

                print(
                    "Failed:",
                    tournament_id,
                    e
                )

            else:

                time.sleep(5)



    name = (
        tournament.get("name")
        or tournament.get("fullName")
        or tournament_id
    )


    print(
        name,
        "-",
        len(players),
        "players"
    )


    time.sleep(
        random.uniform(1, 2)
    )


    return tournament, players




# ----------------------------------
# MAIN
# ----------------------------------


team_members = get_team_members()


print(
    "Current team members:",
    len(team_members)
)



tournaments = get_team_tournaments()


print(
    "Found tournaments:",
    len(tournaments)
)



print(
    "Downloading results..."
)



results = []


with ThreadPoolExecutor(
    max_workers=2
) as executor:


    jobs = [

        executor.submit(
            get_tournament_results,
            tournament
        )

        for tournament in tournaments

    ]


    for job in as_completed(jobs):

        results.append(
            job.result()
        )





# ----------------------------------
# CALCULATE ALL SCORES
# ----------------------------------


print()
print("Processing players...")


total_entries = 0


for tournament, players in results:


    for player in players:


        username = player.get(
            "username"
        )


        if not username:
            continue



        total_entries += 1



        leaderboard[username]["points"] += player.get(
            "score",
            0
        )


        leaderboard[username]["tournaments"] += 1



        if player.get("rank") == 1:

            leaderboard[username]["wins"] += 1






# ----------------------------------
# CLEANUP NON TEAM MEMBERS
# ----------------------------------


print()
print("Cleaning leaderboard...")


final_players = []

removed = 0



for username, stats in leaderboard.items():


    if username.lower() not in team_members:

        removed += 1

        continue



    final_players.append({

        "username": username,

        "points": stats["points"],

        "tournaments": stats["tournaments"],

        "wins": stats["wins"]

    })



print(
    "Removed outsiders:",
    removed
)



# SORT

final_players.sort(
    key=lambda x: x["points"],
    reverse=True
)




# ----------------------------------
# SAVE JSON
# ----------------------------------


output = {

    "team": TEAM_ID,

    "updated": datetime.now().isoformat(),

    "total_players": len(final_players),

    "total_entries_processed": total_entries,

    "players": final_players

}



with open(
    "leaderboard.json",
    "w",
    encoding="utf-8"
) as f:


    json.dump(
        output,
        f,
        indent=4,
        ensure_ascii=False
    )




print()
print("==============================")
print("Leaderboard updated!")
print(
    "Players:",
    len(final_players)
)
print(
    "Saved: leaderboard.json"
)
print("==============================")