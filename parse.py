#!/usr/bin/env python3
import struct
import constants
import os.path as path
import sys

def helptext():
    print(f"Usage: `python3 {sys.argv[0]} <path to cmRally.cfg>`")

if not len(sys.argv) == 2:
    helptext()
    exit(1)

if not path.exists(sys.argv[1]):
    helptext()
    exit(1)

with open(sys.argv[1], "rb") as savefile:
    data = savefile.read()

if not len(data) == 7712:
    helptext()
    exit(1)

stage_records_chunk = data[4092:6162]
stage_record_size = 30
n_stage_records = len(stage_records_chunk) // stage_record_size

def parse_name(byte_values):
    name = ""
    for val in byte_values:
        if val == 0: break
        name += chr(val)
    return name

def format_time(hundredths):
    minutes = hundredths // 6000
    hundredths = hundredths - minutes*6000
    seconds = hundredths // 100
    hundredths = hundredths - seconds*100
    return f"{minutes:02d}:{seconds:02d}.{hundredths:02d}"
    
print("STAGE TIMES "+'-'*114)
for (i, stage_name) in enumerate(constants.CMR_STAGE_NAMES):
    # Some fields are left blank in the save file
    if not stage_name: continue
    rally_name = constants.CMR_RALLY_NAMES[i // 7]


    byte_values = stage_records_chunk[stage_record_size*i : stage_record_size*(i+1)]

    name, split_times, metadata = byte_values[:12], byte_values[12:28], byte_values[28:]
    name = parse_name(name)
    split_times = struct.unpack("<"+"H"*8, split_times)

    # Special stages have no checkpoint times
    if i in constants.CMR_SPECIAL_STAGES:
        split_times = split_times[-1:]

    time_strings = map(format_time, split_times)
    metadata, = struct.unpack("<H", metadata)

    car_id = metadata & 0x000F
    metadata >>= 4
    if car_id in constants.CMR_CAR_NAMES:
        car_id = constants.CMR_CAR_NAMES[car_id]

    player = metadata & 0x1
    metadata >>= 1

    manual = metadata & 0x1
    metadata >>= 1

    print('%13s'%rally_name, 
        '%-5s'%stage_name, 
        '%12s'%name, 
        '%71s'%' '.join(list(time_strings)),
        format(metadata, "011b"),
        car_id,
        "M" if manual else "A")

rally_chunk = data[3452:4092]
rally_chunk_size = 16
n_rally_records = len(rally_chunk) // rally_chunk_size

print("RALLY TIMES "+'-'*114)
for i in range(n_rally_records):
    rally_name = constants.CMR_RALLY_NAMES[i // 5]
    position = ["1st","2nd","3rd","4th","5th"][i % 5]

    byte_values = rally_chunk[rally_chunk_size*i : rally_chunk_size*(i+1)]

    name, metadata = byte_values[:12], byte_values[12:]
    name = parse_name(name)
    metadata = int.from_bytes(metadata, byteorder='little', signed=False)
    time = metadata & 0x0007FFFF
    metadata >>= 19
    
    car_id = (metadata & 0x00F)
    metadata >>= 4
    if car_id in constants.CMR_CAR_NAMES:
        car_id = constants.CMR_CAR_NAMES[car_id]

    player = metadata & 0x1
    metadata >>= 1

    manual = metadata & 0x1
    metadata >>= 1

    print('%13s'%rally_name,
        position,
        '%12s'%name, 
        format_time(time), 
        format(metadata, "05b"), 
        car_id,
        "M" if manual else "A")
