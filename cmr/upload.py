#!/usr/bin/env python3
import os
import requests
import hashlib
import pickle
from dotenv import load_dotenv
from decode import read_rally_times, read_stage_times

UPLOADS_FILE = "./hashes.pickle"

def record_hash(record):
    fields = ["Player","Car","Game","Rally","Stage"]
    s = ",".join(map(str,record["Times"]))
    s = "".join(record[f] for f in fields) + s
    md5 = hashlib.md5()
    md5.update(s.encode("utf-8"))
    return md5.hexdigest()

def upload_times(api_url, api_key, game_path):
    cfg_path = os.path.expanduser(os.path.join(game_path, "save/cmRally.cfg"))

    with open(cfg_path, "rb") as f:
        game_data = f.read()

    if not len(game_data) == 7712:
        print("Unexpected file size for cmRally.cfg")
        exit(1)

    if os.path.exists(UPLOADS_FILE):
        with open(UPLOADS_FILE, "rb") as f:
            uploaded_hashes = pickle.load(f)
    else:
        uploaded_hashes = set()

    print("-- UPLOADING STAGE TIMES --")
    for record in read_stage_times(game_data):
        h = record_hash(record)
        if record["Human"] and h not in uploaded_hashes:
            post_data = {
                "player": record["Player"],
                "game": record["Game"],
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

            uploaded_hashes.add(h)

    print("-- UPLOADING RALLY TIMES --")
    for record in read_rally_times(game_data):
        h = record_hash(record)
        if record["Human"] and h not in uploaded_hashes:
            post_data = {
                "player": record["Player"],
                "game": record["Game"],
                "rally": record["Rally"],
                "stage": record["Stage"],
                "splits": [],
                "time": record["Times"][0],
                "car": record["Car"],
                "manual": record["Manual"]
            }

            print(post_data)
            r = requests.post(api_url, json=post_data, headers={"x-api-key": api_key})
            r.raise_for_status()

            uploaded_hashes.add(h)

    with open(UPLOADS_FILE, 'wb') as f:
        pickle.dump(uploaded_hashes, f)

if __name__ == "__main__":
    load_dotenv()

    api_key = os.environ["LEADERBOARD_API_KEY"]
    api_url = os.environ["LEADERBOARD_API_URL"]
    game_path = os.environ["CMR_INSTALL_PATH"]
    if not api_key or not api_url or not game_path:
        print("Missing environment values (see .env)")
        exit(1)

    upload_times(api_key, api_url, game_path)
