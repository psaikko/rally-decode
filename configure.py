#!/usr/bin/env python3

game_path = input("Game path: ")
api_url = input("API URL: ")
api_key = input("API Key: ")

with open(".env", "w") as f:
    print(f"""\
LEADERBOARD_API_URL="{api_url}"
LEADERBOARD_API_KEY="{api_key}"
CMR_INSTALL_PATH="{game_path}"
""", end='', file=f)
