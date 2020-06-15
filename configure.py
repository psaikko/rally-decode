#!/usr/bin/env python3

cmr_path = input("CMR path: ")
cmr2_path = input("CMR2 path: ")
api_url = input("API URL: ")
api_key = input("API Key: ")

with open(".env", "w") as f:
    print("""\
LEADERBOARD_API_URL="%s"
LEADERBOARD_API_KEY="%s"
CMR_INSTALL_PATH="%s"
CMR2_INSTALL_PATH="%s"
""" % (api_url, api_key, cmr_path, cmr2_path), end='', file=f)
