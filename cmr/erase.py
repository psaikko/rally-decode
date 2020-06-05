#!/usr/bin/env python3
import struct
import constants
import os
from dotenv import load_dotenv
from decode import read_rally_times, read_stage_times, format_time
from shutil import copyfile

def create_meta(car_id, is_manual, is_human):
    meta = 0x0000
    meta |= car_id
    human_bit = 1<<4 if is_human else 0
    manual_bit = 1<<5 if is_manual else 0
    meta |= human_bit
    meta |= manual_bit
    return meta

def clear_stage_times(savefile_data):
    data_bytearray = bytearray(savefile_data)
    stage_chunk_start = 4092
    stage_record_size = 30
    for (i, stage_name) in enumerate(constants.CMR_STAGE_NAMES):
        # Some fields are left blank in the save file
        if not stage_name: continue
        m = (60 * 100) # one minute
        meta = create_meta(0, 0, 0)
        name = b"DELETED\0\0\0\0\0"
        byte_values = bytearray(30)
        struct.pack_into("<12sHHHHHHHHH", byte_values, 0, name, m, m*2, m*3, m*4, m*5, m*6, m*7, m*8, meta)
        data_bytearray[stage_chunk_start + stage_record_size*i : stage_chunk_start + stage_record_size*(i+1)] = byte_values
    return bytes(data_bytearray)

def clear_savefile(game_path):
    cfg_path = os.path.expanduser(os.path.join(game_path, "save/cmRally.cfg"))
    backup_path = os.path.expanduser(os.path.join(game_path, "save/backup.cfg"))
    # Make a backup copy of the config file. Overwrites old backup.
    copyfile(cfg_path, backup_path)

    if not os.path.exists(cfg_path):
        print("Could not find cmRally.cfg at", cfg_path)
        exit(1)

    with open(cfg_path, "rb") as savefile:
        data = savefile.read()

    if not len(data) == 7712:
        print("Unexpected size %d for cmRally.cfg file" % len(data))
        exit(1)

    data = clear_stage_times(data)

    with open(cfg_path, "wb") as savefile:
        savefile.write(data)


if __name__ == "__main__":
    load_dotenv()

    game_path = os.environ["CMR_INSTALL_PATH"]

    if not game_path:
        print("Missing environment values (see .env)")
        exit(1)

    clear_savefile(game_path)
    print("Erased stage times")
