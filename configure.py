#!/usr/bin/env python3

cmr_path = input("CMR path: ")
cmr2_path = input("CMR2 path: ")
api_url = input("API URL: ")
api_key = input("API Key: ")

with open(".env", "w") as f:
    print(f"""\
LEADERBOARD_API_URL="{api_url}"
LEADERBOARD_API_KEY="{api_key}"
CMR_INSTALL_PATH="{cmr_path}"
CMR2_INSTALL_PATH="{cmr2_path}"
""", end='', file=f)
