#!/usr/bin/env python3
import struct
import constants
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
    stage_records_chunk = savefile_data[1784:2488]
    stage_record_size = 8

    stage_splits_chunk = savefile_data[2488:4248]
    split_record_size = 20

    n_stage_records = len(stage_records_chunk) // stage_record_size

    print(n_stage_records)

    stage_data = []
    for (i, stage_name) in enumerate(constants.CMR2_STAGE_NAMES):

        if not stage_name: continue

        rally_name = constants.CMR2_RALLY_NAMES[i // 11]

        byte_values = stage_records_chunk[stage_record_size*i : stage_record_size*(i+1) - 1]

        split_bytes = stage_splits_chunk[split_record_size*i : split_record_size*(i+1)]

        fields = struct.unpack("<3sL", byte_values)
        player_name = parse_name(fields[0])
        stage_time = fields[1] >> 15
        metadata = (fields[1] >> 8 & 0x7F)

        car = constants.CMR2_CAR_NAMES[metadata & 0x0F]
        automatic = metadata & 0x40

        splits = struct.unpack("<HHHHHHHH", split_bytes[2:-2])

        stage_data.append({
            'Game': 'CMR2',
            'Rally': rally_name,
            "Stage": stage_name,
            'Player': player_name,
            'Splits': splits,
            'Time': stage_time,
            'Car': car,
            'Manual': not automatic
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
        metadata = (fields[1] >> 8 & 0x7F)

        car = constants.CMR2_CAR_NAMES[metadata & 0x0F]
        automatic = metadata & 0x40

        splits = struct.unpack("<HHHHHH", split_bytes)

        stage_data.append({
            'Game': 'CMR2',
            'Rally': "Arcade",
            "Stage": constants.CMR2_ARCADE_STAGES[i],
            'Player': player_name,
            'Splits': splits,
            'Time': stage_time,
            'Car': car,
            'Manual': not automatic
        })
    return stage_data

def read_rally_times(savefile_data):
    rally_chunk = savefile_data[3452:4092]
    rally_chunk_size = 16
    n_rally_records = len(rally_chunk) // rally_chunk_size
    rally_times = []
    for i in range(n_rally_records):
        rally_name = constants.CMR2_RALLY_NAMES[i // 5]
        rank = (i % 5) + 1

        byte_values = rally_chunk[rally_chunk_size*i : rally_chunk_size*(i+1)]

        player_name, metadata = struct.unpack("<12sI", byte_values)
        player_name = parse_name(player_name)
        time = metadata & 0x0007FFFF
        metadata >>= 19
        (car_id, is_manual, is_human) = parse_meta(metadata)

        rally_times.append({
            "Game": "CMR2",
            "Rally": rally_name,
            "Stage": "Rally",
            "Rank": rank,
            "Player": player_name,
            "Times": [time >> 8],
            "Car": constants.CMR2_CAR_NAMES[car_id],
            "Manual": is_manual,
            "Human": is_human
        })
    return rally_times
        

if __name__ == "__main__":
    if not len(sys.argv) == 2:
        helptext()
        exit(1)

    if not path.exists(sys.argv[1]):
        helptext()
        exit(1)

    with open(sys.argv[1], "rb") as savefile:
        data = savefile.read()

    if not len(data) == 14748:
        helptext()
        exit(1)

    print("-- STAGE TIMES --")
    for record in read_stage_times(data):
        print('%15s' % record["Rally"], 
              '%13s' % record["Stage"], 
              '%4s' % record["Player"], 
              '%9s' % format_time(record["Time"]),
              '%70s' % ' '.join(map(format_time, record["Splits"])),
              '%10s' % record["Car"],
              'M' if record['Manual'] else 'A')

    print("-- ARCADE TIMES --")
    for record in read_arcade_times(data):
        print('%7s' % record["Rally"], 
              '%15s' % record["Stage"], 
              '%4s' % record["Player"], 
              '%9s' % format_time(record["Time"]),
              '%70s' % ' '.join(map(format_time, record["Splits"])),
              '%10s' % record["Car"],
              'M' if record['Manual'] else 'A')

    print("\n-- RALLY TIMES --")
    for record in read_rally_times(data):
        print('%13s' % record["Rally"],
              record["Rank"],
              '%12s' % record["Player"], 
              format_time(record["Times"][0]),
              record["Car"],
              "M" if record["Manual"] else "A")

    

    