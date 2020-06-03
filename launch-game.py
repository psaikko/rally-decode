#!/usr/bin/env python3
import os
import shutil
import platform
import subprocess
from dotenv import load_dotenv
from erase import clear_savefile
from upload import upload_times

load_dotenv()

IS_WINDOWS = "Windows" in platform.system()
GAME_DIR = os.environ["CMR_INSTALL_PATH"]
API_KEY = os.environ["LEADERBOARD_API_KEY"]
API_URL = os.environ["LEADERBOARD_API_URL"]
EXE_PATH = os.path.expanduser(os.path.join(GAME_DIR, "Rally.exe"))

if not API_KEY or not API_URL or not GAME_DIR:
    print("Missing environment values (see configure.py)")
    exit(1)

if not os.path.exists(EXE_PATH):
    print("Could not find Game.exe in", GAME_DIR)
    exit(1)

if not IS_WINDOWS and shutil.which("wine") == None:
    print("Wine not detected")
    exit(1)

try:
    clear_savefile(GAME_DIR)

    cmd = [EXE_PATH]
    if not IS_WINDOWS:
        cmd = ["wine"] + cmd
    subprocess.Popen(cmd, stderr=subprocess.DEVNULL).communicate()

    if not IS_WINDOWS:
        subprocess.Popen(["wineserver","--wait"]).communicate()

    upload_times(API_URL, API_KEY, GAME_DIR)

except Exception as e:
    print(e)