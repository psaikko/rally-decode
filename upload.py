#!/usr/bin/env python3
import os
import requests
import hashlib
import pickle
from dotenv import load_dotenv
import cmr.decode
import cmr2.decode

UPLOADS_FILE = "./hashes.pickle"

def record_hash(record):
    fields = ["Player","Car","Game","Rally","Stage"]
    s = ",".join(map(str,record["Times"]))
    s = "".join(record[f] for f in fields) + s
    md5 = hashlib.md5()
    md5.update(s.encode("utf-8"))
    return md5.hexdigest()

def upload_cmr(api_url, api_key, game_path):
    cfg_path = os.path.expanduser(os.path.join(game_path, "save/cmRally.cfg"))
    game_data = cmr.decode.read_save_bytes(cfg_path)

    print("-- UPLOADING CMR STAGE TIMES --")
    upload_times(api_url, api_key, cmr.decode.read_stage_times(game_data))

    print("-- UPLOADING CMR RALLY TIMES --")
    upload_times(api_url, api_key, cmr.decode.read_rally_times(game_data))

def upload_cmr2(api_url, api_key, game_path):
    cfg_path = os.path.expanduser(os.path.join(game_path, "Configuration/GameInfo.rcf"))
    game_data = cmr2.decode.read_save_bytes(cfg_path)

    print("-- UPLOADING CMR2 STAGE TIMES --")
    upload_times(api_url, api_key, cmr2.decode.read_stage_times(game_data))

    print("-- UPLOADING CMR2 ARCADE TIMES --")
    upload_times(api_url, api_key, cmr2.decode.read_arcade_times(game_data))

    print("-- UPLOADING CMR2 RALLY TIMES --")
    upload_times(api_url, api_key, cmr2.decode.read_rally_times(game_data))

def upload_times(api_url, api_key, records):
    if os.path.exists(UPLOADS_FILE):
        with open(UPLOADS_FILE, "rb") as f:
            uploaded_hashes = pickle.load(f)
    else:
        uploaded_hashes = set()

    for record in records:
        h = record_hash(record)
        if record["Human"] and h not in uploaded_hashes:
            splits = record["Times"]
            time = splits[-1]
            if len(splits) < 2: splits = []
            post_data = {
                "player": record["Player"],
                "game": record["Game"],
                "rally": record["Rally"],
                "stage": record["Stage"],
                "splits": splits,
                "time": time,
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
    cmr_path = os.environ["CMR_INSTALL_PATH"]
    cmr2_path = os.environ["CMR2_INSTALL_PATH"]

    if not api_key or not api_url or not (cmr_path or cmr2_path):
        print("Missing environment values (see configure.py)")
        exit(1)

    if cmr_path:
        upload_cmr(api_url, api_key, cmr_path)

    if cmr2_path:
        upload_cmr2(api_url, api_key, cmr2_path)
