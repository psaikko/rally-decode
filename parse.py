#!/usr/bin/env python3
import struct

with open("cmRally.cfg", "rb") as savefile:
    data = savefile.read()

car_names = {
    21: 'Ford Escort MK II',
    22: 'Mitsubishi Lancer E4',
    16: 'Subaru Impreza WRC',
    26: 'Ford Escort WRC',
    25: 'Toyota Corolla WRC',
    27: 'Renault Maxi Megane',
    23: 'VW Golf GTI Kit Car',
    18: 'Skoda Felicia Kit Car',
    17: 'Seat Ibiza Kit Car EVO2'
}

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
    
for i in range(n_stage_records):
    byte_values = stage_records_chunk[stage_record_size*i : stage_record_size*(i+1)]

    name, split_times, metadata = byte_values[:12], byte_values[12:28], byte_values[28:]
    name = parse_name(name)
    split_times = struct.unpack("<"+"H"*8, split_times)
    time_strings = map(format_time, split_times)
    metadata, = struct.unpack("<H", metadata)

    car_id = metadata & 0x001F
    metadata >>= 5
    if car_id in car_names:
        car_id = car_names[car_id]

    manual = metadata & 0x1
    metadata >>= 1

    print('%12s'%name, ' '.join(list(time_strings)), format(metadata, "011b"), car_id, "Manual" if manual else "Automatic")

rally_chunk = data[3452:4092]
rally_chunk_size = 16
n_rally_records = len(rally_chunk) // rally_chunk_size

for i in range(n_rally_records):
    byte_values = rally_chunk[rally_chunk_size*i : rally_chunk_size*(i+1)]

    name, metadata = byte_values[:12], byte_values[12:]
    name = parse_name(name)
    metadata = int.from_bytes(metadata, byteorder='little', signed=False)
    time = metadata & 0x0007FFFF
    metadata >>= 19
    
    car_id = (metadata & 0x01F)
    metadata >>= 5
    if car_id in car_names:
        car_id = car_names[car_id]

    manual = metadata & 0x1
    metadata >>= 1

    print(name, format_time(time), format(metadata, "05b"), car_id, "Manual" if manual else "Automatic")