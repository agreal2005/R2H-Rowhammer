"""Fixed trace generator — ensure LLC receives enough traffic."""
import struct, os

def make_instr(addr, ip=0):
    return struct.pack('<QBB2s4sQQQQQQ', ip, 0, 0, b'\x00'*2, b'\x00'*4, 0, 0, addr, 0, 0, 0)

def read_unique(path):
    with open(path) as f:
        return list(dict.fromkeys(int(l.strip(),16) for l in f if l.strip()))

# Generate traces with heavy repetition
trad = read_unique("traces/trad_rh/trad_rh.trace")
r2h = read_unique("traces/r2h/r2h.trace")

print(f"Trad unique: {len(trad)}, R2H unique: {len(r2h)}")

# For Trad-RH: 17 addrs, repeat 100000 times = 1.7M instructions
with open("traces/trad_rh/trad_rh.champsim", 'wb') as f:
    for _ in range(100000):
        for a in trad:
            f.write(make_instr(a))
print(f"Trad-RH: 17 x 100000 = {1700000} instructions")

# For R2H: 4096 addrs, repeat 500 times = 2M instructions
with open("traces/r2h/r2h.champsim", 'wb') as f:
    for _ in range(500):
        for a in r2h:
            f.write(make_instr(a))
print(f"R2H: 4096 x 500 = {4096*500} instructions")
