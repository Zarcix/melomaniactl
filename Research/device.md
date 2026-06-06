# Device Bit Ordering

## Sample Packet
AA BB BB BB BB BB BB BB BB BB BBB BB BB BB BB BB BB BB BB B BB CC CC CC CC DD
02 4d 61 63 42 6f 6f 6b 20 50 72 6f 20 37 35 30 65 64 35 38 00 57 46 c6 54 00
01 55 47 52 45 45 4e 2d 42 54 37 30 31 00 00 00 00 00 00 00 00 5b 4e f6 00 00
03 61 20 75 68 68 68 20 70 68 6f 6e 65 20 75 68 68 68 20 79 65 2c 59 75 79 00
04 64 61 6c 61 6d 61 62 6f 6e 6b 00 00 00 00 00 00 00 00 00 00 28 21 9a 61 02

## Packet Breakdown
AA BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB CCCCCCCC DD

A = Connection or maybe pairing order (?)
B = Device Name
C = Mac Address (last 4 in a weird order. if AA:BB:CC:DD, order is AA:DD:CC:BB)
D = Connection Status (0 = Paired, 1 = Connected, 2 = Connected Primary)