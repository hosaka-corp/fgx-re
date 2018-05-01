#!/usr/bin/python

import os, sys
import hexdump
import struct
import binascii

from fgx_format import *
from fgx_encode import *

if len(sys.argv) < 4:
    print("Usage: garage-fuzz.py <filename> <33216 bytes of raw garage data> <output filename>")
    exit(0)
else:
    filename = sys.argv[1]
    garage_data_file = sys.argv[2]
    output_filename = sys.argv[3]

garage_size = os.stat(garage_data_file).st_size
print("garage data is {} bytes".format(garage_size))
if (garage_size != 33216):
    print("Garage file must be 33216 bytes :^(")
    exit(-1)

# Import a GCI
input_gci = gci(filename)
print("Forcing region to NTSC")
input_gci.set_region(region.ntsc)
print(input_gci.get_filename())

# Decode the replay data, get decoded representation of data
my_decoder = decoder(input_gci.get_replay_data())
my_replay = my_decoder.dump()

if (my_replay.player_array_dict[0]['is_custom_ship'] == 0):
    print("This GCI doesn't have garage data. Nice.")
    exit(-1)

# Switch out garage data takes a bytearray of DECODED garage data
#new_garage_data = bytearray(b'\x4b'*33216)

with open(garage_data_file, "rb") as f:
    new_garage_data = bytearray(f.read())

my_replay.player_array_dict[0]['custom_ship_data'] = new_garage_data 

# -----------------------------------------------------------------------------

# Re-encode the replay data
my_encoder = encoder()
new_replay_data = my_encoder.encode_gci(my_replay)

# Concatenate new replay data to the rest of the original GCI
input_gci.set_replay_data(new_replay_data)

# Recompute the checksum of the whole GCI
input_gci.recompute_checksum()

# Write the new GCI to a file
print("Writing to {}".format(output_filename))
ofd = open(output_filename, "wb")
ofd.write(input_gci.raw_bytes)
ofd.close()
