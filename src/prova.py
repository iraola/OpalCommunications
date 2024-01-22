import struct

value = 3.14
data_packed = struct.pack('!f', value)
value_unpacked = struct.unpack('!f', data_packed)[0]
print(data_packed)