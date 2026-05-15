"""Final trace generator: creates enough unique addresses to overflow L1D/L2C"""
import struct

def make_instr(addr):
    return struct.pack('<QBB2s4sQQQQQQ', 0, 0, 0, b'\x00'*2, b'\x00'*4, 0, 0, addr, 0, 0, 0)

# R2H already has 3072 unique addresses — this overflows L1D (768 blocks) and L2C (8192 blocks? No, 1024 sets x 8 ways = 8192 blocks, 512KB)
# 3072 addrs = 192KB. Fits in L2C. Need >8192 unique addrs to overflow L2C.
# But 3072 > L1D ways per set... Actually all our addrs map to DIFFERENT sets.
# Each address goes to a different L1D set. So no L1D conflicts!
# L1D has 64 sets. 3072 addrs / 64 sets = 48 per set. L1D has 12 ways. So L1D overflows per set!

# For Trad-RH: 17 addrs all in L1D set 0. L1D set 0 has 12 ways. 17 > 12 = overflow!
# But after 17 accesses, L1D set 0 has all 17 blocks. Next access: evicts one, miss goes to L2C.
# L2C set 0 also has 17 unique blocks in 8 ways = overflow.
# But ChampSim's LRU might be serving hits from the non-evicted blocks?

# The problem is ChampSim might be counting L1D/L2C hits from blocks that were filled during warmup.
# Let's check: run without warmup and see per-cache stats.

print("Running full stats dump...")
