#!/usr/bin/env python3
import struct
from . import constants
import os.path as path
import sys

def helptext():
    print(f"Usage: `python3 {sys.argv[0]} <path to GameInfo.rcf>`")

def parse_name(byte_values):
    name = ""
    for val in byte_values:
        if val == 0: break
        name += chr(val)
    return name

def parse_meta(meta):
    car_id = meta & 0b0011111
    automatic = meta & 0b1000000
    return (car_id, not automatic)

def format_time(hundredths):
    minutes = hundredths // 6000
    hundredths = hundredths - minutes*6000
    seconds = hundredths // 100
    hundredths = hundredths - seconds*100
    return f"{minutes:02d}:{seconds:02d}.{hundredths:02d}"
    
def read_stage_times(savefile_data):
    stage_records_chunk = savefile_data[1784:2488]
    stage_record_size = 8

    stage_splits_chunk = savefile_data[2488:4248]
    split_record_size = 20

    n_stage_records = len(stage_records_chunk) // stage_record_size

    stage_data = []
    for (i, stage_name) in enumerate(constants.CMR2_STAGE_NAMES):

        if not stage_name: continue

        rally_name = constants.CMR2_RALLY_NAMES[i // 11]

        byte_values = stage_records_chunk[stage_record_size*i : stage_record_size*(i+1) - 1]

        split_bytes = stage_splits_chunk[split_record_size*i : split_record_size*(i+1)]

        fields = struct.unpack("<3sL", byte_values)
        player_name = parse_name(fields[0])
        stage_time = fields[1] >> 15

        car_id, is_manual = parse_meta(fields[1] >> 8)

        splits = struct.unpack("<HHHHHHHH", split_bytes[2:-2])

        stage_data.append({
            'Game': 'CMR2',
            'Rally': rally_name,
            "Stage": stage_name,
            'Player': player_name,
            'Times': splits,
            'Car': constants.CMR2_CAR_NAMES[car_id],
            'Manual': is_manual,
            "Human": player_name != "cmr"
        })
    return stage_data

def read_arcade_times(savefile_data):
    arcade_records_chunk = savefile_data[4788:4854]
    arcade_record_size = 8

    arcade_splits_chunk = savefile_data[4860:]
    split_record_size = 12

    n_arcade_records = len(arcade_records_chunk) // arcade_record_size

    stage_data = []
    for i in range(n_arcade_records):

        byte_values = arcade_records_chunk[arcade_record_size*i : arcade_record_size*(i+1) - 1]

        split_bytes = arcade_splits_chunk[split_record_size*i : split_record_size*(i+1)]

        fields = struct.unpack("<3sL", byte_values)

        player_name = parse_name(fields[0])
        stage_time = fields[1] >> 15

        car_id, is_manual = parse_meta(fields[1] >> 8)

        splits = struct.unpack("<xxHHHxxxx", split_bytes)
        splits += (stage_time,)

        stage_data.append({
            'Game': 'CMR2',
            'Rally': constants.CMR2_ARCADE_RALLIES[i],
            "Stage": "Arcade",
            'Player': player_name,
            'Times': list(splits),
            'Car': constants.CMR2_CAR_NAMES[car_id],
            'Manual': is_manual,
            "Human": player_name != "cmr"
        })
    return stage_data

def read_rally_times(savefile_data):
    rally_chunk = savefile_data[344:1784]
    rally_chunk_size = 12
    rally_times = []

    n_difficulties = 3
    n_rallies = len(constants.CMR2_RALLY_NAMES)
    n_times_per_rally = 5

    for i in range(n_difficulties * n_rallies * n_times_per_rally):
        i_rally = i // (n_difficulties * n_times_per_rally)
        i_difficulty = i % (n_difficulties * n_times_per_rally) // n_times_per_rally
        difficulty = constants.DIFFICULTIES[i_difficulty]
        rank = (i % 5) + 1

        rally_name = constants.CMR2_RALLY_NAMES[i_rally]
        byte_values = rally_chunk[rally_chunk_size*i : rally_chunk_size*(i+1)]

        name, meta, time = struct.unpack("<4sHxxI", byte_values)
        player_name = parse_name(name)

        car_id, is_manual = parse_meta(meta)

        rally_times.append({
            "Game": "CMR2",
            "Rally": rally_name,
            "Stage": f"Rally-{difficulty}",
            "Rank": rank,
            "Player": player_name,
            "Times": [time],
            "Car": constants.CMR2_CAR_NAMES[car_id],
            "Manual": is_manual,
            "Human": player_name != "cmr"
        })
    return rally_times
        
def read_save_bytes(fp):
    if not path.exists(fp):
        print(fp, "not found")
        exit(1)

    with open(fp, "rb") as savefile:
        data = savefile.read()

    if not len(data) == 14748:
        print("Unexpected size for GameInfo.rcf")
        exit(1)

    return data

if __name__ == "__main__":
    if not len(sys.argv) == 2:
        helptext()
        exit(1)

    data = read_save_bytes(sys.argv[1])

    print("-- STAGE TIMES --")
    for record in read_stage_times(data):
        if record["Human"]:
            print('%15s' % record["Rally"], 
                '%13s' % record["Stage"], 
                '%4s' % record["Player"], 
                '%9s' % format_time(record["Times"][-1]),
                '%70s' % ' '.join(map(format_time, record["Times"])),
                '%10s' % record["Car"],
                'M' if record['Manual'] else 'A')

    print("-- ARCADE TIMES --")
    for record in read_arcade_times(data):
        if record["Human"]:
            print('%7s' % record["Rally"], 
                '%15s' % record["Stage"], 
                '%4s' % record["Player"], 
                '%9s' % format_time(record["Times"][-1]),
                '%70s' % ' '.join(map(format_time, record["Times"])),
                '%10s' % record["Car"],
                'M' if record['Manual'] else 'A')

    print("\n-- RALLY TIMES --")
    for record in read_rally_times(data):
        if record["Human"]:    
            print('%15s' % record["Rally"],
                '%10s' % record["Stage"], 
                record["Rank"],
                '%12s' % record["Player"],
                '%9s' % format_time(record["Times"][0]),
                '%10s' % record["Car"],
                'M' if record['Manual'] else 'A')

