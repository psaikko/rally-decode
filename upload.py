#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv
from decode import read_rally_times, read_stage_times

load_dotenv()

api_key = os.environ["LEADERBOARD_API_KEY"]
api_url = os.environ["LEADERBOARD_API_URL"]
game_path = os.environ["CMR_INSTALL_PATH"]
if not api_key or not api_url or not game_path:
    print("Missing environment values (see .env)")
    exit(1)

cfg_path = os.path.expanduser(os.path.join(game_path, "save/cmRally.cfg"))

with open(cfg_path, "rb") as f:
    game_data = f.read()

if not len(game_data) == 7712:
    print("Unexpected file size for cmRally.cfg")
    exit(1)

print("-- UPLOADING STAGE TIMES --")
for record in read_stage_times(game_data):
    if record["Human"]:
        post_data = {
            "player": record["Player"],
            "game": "CMR",
            "rally": record["Rally"],
            "stage": record["Stage"],
            "splits": record["Times"],
            "time": record["Times"][-1],
            "car": record["Car"],
            "manual": record["Manual"]
        }
        print(post_data)
        r = requests.post(api_url, json=post_data, headers={"x-api-key": api_key})
        r.raise_for_status()

print("-- UPLOADING RALLY TIMES --")
for record in read_rally_times(game_data):
    if record["Human"]:
        post_data = {
            "player": record["Player"],
            "game": "CMR",
            "rally": record["Rally"],
            "stage": "Rally",
            "splits": [],
            "time": record["Time"],
            "car": record["Car"],
            "manual": record["Manual"]
        }
        print(post_data)
        r = requests.post(api_url, json=post_data, headers={"x-api-key": api_key})
        r.raise_for_status()