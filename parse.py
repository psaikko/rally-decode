#!/usr/bin/env python3

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

def bytes_to_short(byte_values):
    shorts = []
    for i in range(len(byte_values)//2):
        shorts.append(byte_values[i*2] + byte_values[i*2+1]*256)
    return shorts

def format_time(hundredths):
    minutes = hundredths // 6000
    hundredths = hundredths - minutes*6000
    seconds = hundredths // 100
    hundredths = hundredths - seconds*100
    return f"{minutes:02d}:{seconds:02d}.{hundredths:02d}"
    
for i in range(n_stage_records):
    data_i = stage_records_chunk[stage_record_size*i : stage_record_size*(i+1)]
    byte_values = [int(b) for b in data_i]

    name, byte_values = byte_values[:12], byte_values[12:]
    name = parse_name(name)

    split_times, byte_values = byte_values[:16], byte_values[16:]
    split_times = bytes_to_short(split_times)
    time_strings = map(format_time, split_times)

    print(name, list(time_strings), byte_values)