#!/usr/bin/env python3
import struct
from . import constants
import os.path as path
import sys

def helptext():
    print(f"Usage: `python3 {sys.argv[0]} <path to cmRally.cfg>`")

def parse_name(byte_values):
    name = ""
    for val in byte_values:
        if val == 0: break
        name += chr(val)
    return name

def parse_meta(data):
    car_id = data & 0x000F
    data >>= 4
    is_human = data & 0x1
    data >>= 1
    is_manual = data & 0x1
    data >>= 1
    return (car_id, is_manual, is_human)

def format_time(hundredths):
    minutes = hundredths // 6000
    hundredths = hundredths - minutes*6000
    seconds = hundredths // 100
    hundredths = hundredths - seconds*100
    return f"{minutes:02d}:{seconds:02d}.{hundredths:02d}"
    
def read_stage_times(savefile_data):
    stage_records_chunk = savefile_data[4092:6162]
    stage_record_size = 30
    n_stage_records = len(stage_records_chunk) // stage_record_size
    stage_data = []
    for (i, stage_name) in enumerate(constants.CMR_STAGE_NAMES):
        # Some fields are left blank in the save file
        if not stage_name: continue
        rally_name = constants.CMR_RALLY_NAMES[i // 7]

        byte_values = stage_records_chunk[stage_record_size*i : stage_record_size*(i+1)]
        fields = struct.unpack("<12sHHHHHHHHH", byte_values)
        player_name = parse_name(fields[0])
        split_times = fields[1:9]
        metadata = fields[9]

        # Special stages have no checkpoint times
        if i in constants.CMR_SPECIAL_STAGES:
            split_times = split_times[-1:]

        (car_id, is_manual, is_human) = parse_meta(metadata)

        stage_data.append({
            'Game': 'CMR',
            'Rally': rally_name,
            'Stage': stage_name,
            'Player': player_name,
            'Times': split_times,
            'Car': constants.CMR_CAR_NAMES[car_id],
            'Manual': is_manual,
            'Human': is_human
        })
    return stage_data

def read_rally_times(savefile_data):
    rally_chunk = savefile_data[3452:4092]
    rally_chunk_size = 16
    n_rally_records = len(rally_chunk) // rally_chunk_size
    rally_times = []
    for i in range(n_rally_records):
        rally_name = constants.CMR_RALLY_NAMES[i // 5]
        rank = (i % 5) + 1

        byte_values = rally_chunk[rally_chunk_size*i : rally_chunk_size*(i+1)]

        player_name, metadata = struct.unpack("<12sI", byte_values)
        player_name = parse_name(player_name)
        time = metadata & 0x0007FFFF
        metadata >>= 19
        (car_id, is_manual, is_human) = parse_meta(metadata)

        rally_times.append({
            "Game": "CMR",
            "Rally": rally_name,
            "Stage": "Rally",
            "Rank": rank,
            "Player": player_name,
            "Times": [time],
            "Car": constants.CMR_CAR_NAMES[car_id],
            "Manual": is_manual,
            "Human": is_human
        })
    return rally_times
        
def read_save_bytes(fp):
    if not path.exists(fp):
        print(fp, "not found")
        exit(1)

    with open(fp, "rb") as savefile:
        data = savefile.read()

    if not len(data) == 7712:
        print("Unexpected size for cmRally.cfg")
        exit(1)

    return data

if __name__ == "__main__":
    if not len(sys.argv) == 2:
        helptext()
        exit(1)

    data = read_save_bytes(sys.argv[1])

    print("-- STAGE TIMES --")
    for record in read_stage_times(data):
        print('%13s' % record["Rally"], 
              '%14s' % record["Stage"], 
              '%12s' % record["Player"], 
              '%71s' % ' '.join(map(format_time, record["Times"])),
              record["Car"],
              "M" if record["Manual"] else "A",
              "H" if record["Human"] else "C")

    print("\n-- RALLY TIMES --")
    for record in read_rally_times(data):
        print('%13s' % record["Rally"],
              record["Rank"],
              '%12s' % record["Player"], 
              format_time(record["Times"][0]),
              record["Car"],
              "M" if record["Manual"] else "A")

    

    