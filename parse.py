#!/usr/bin/env python3
import struct

with open("cmRally.cfg", "rb") as savefile:
    data = savefile.read()

print(len(data))

stage_records_chunk = data[4092:6162]

stage_record_size = 30
n_stage_records = len(stage_records_chunk) // stage_record_size

print("Found", n_stage_records, "records")

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
    
for i in range(n_stage_records):
    byte_values = stage_records_chunk[stage_record_size*i : stage_record_size*(i+1)]

    name, split_times, metadata = byte_values[:12], byte_values[12:28], byte_values[28:]
    name = parse_name(name)
    split_times = struct.unpack("<"+"H"*8, split_times)
    time_strings = map(format_time, split_times)

    print(name, list(time_strings), metadata)

rally_chunk = data[3452:4092]
rally_chunk_size = 16
n_rally_records = len(rally_chunk) // rally_chunk_size

for i in range(n_rally_records):
    byte_values = rally_chunk[rally_chunk_size*i : rally_chunk_size*(i+1)]
    name, time_data = byte_values[:12], byte_values[12:]
    name = parse_name(name)
    time_data = int.from_bytes(time_data, byteorder='little', signed=False)
    time = (time_data & 0x000FFFFF)
    data = (time_data & 0xFFF00000) >> 20

    print(name, format_time(time), bin(data))