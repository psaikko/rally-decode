#!/usr/bin/env python3

with open("cmRally.cfg", "rb") as savefile:
    data = savefile.read()

print(len(data))

laprecords = data[4092:6162]

record_size = 30
n_records = len(laprecords) // record_size

print("Found", n_records, "records")

def parse_name(byte_values):
    name = ""
    for val in byte_values:
        if val == 0: break
        name += chr(val)
    return name

for i in range(n_records):
    data_i = laprecords[record_size*i : record_size*(i+1)]
    byte_values = [int(b) for b in data_i]
    name, byte_values = byte_values[:12], byte_values[12:]
    name = parse_name(name)
    print(name, byte_values)