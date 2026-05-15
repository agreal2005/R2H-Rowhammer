"""
Corrected trace generator.
Trad-RH: 17 addrs in set 0, bank 0, rows 0 and 1
R2H: 4096 addrs across sets 0-255, bank 0, rows 0 and 1
"""

TX_OFFSET = 6
NUM_SETS = 2048
BLOCK_SIZE = 64
SET_STRIDE = NUM_SETS * BLOCK_SIZE  # 128KB

def decode(addr):
    a = addr >> TX_OFFSET
    col = a & 0x3FF
    a >>= 10
    bank = a & 0x3
    a >>= 2
    bg = a & 0x3
    a >>= 2
    row = a & 0x1FFFF
    return bg, bank, row, col

def make_addr(row, bank=0, bg=0, col=0):
    return ((row << 14) | (bg << 12) | (bank << 10) | col) << TX_OFFSET

def llc_set(addr):
    return (addr >> 6) & (NUM_SETS - 1)

ROW_A, ROW_B = 0, 1
base_a = make_addr(row=ROW_A, bank=0, col=0)   # 0x0
base_b = make_addr(row=ROW_B, bank=0, col=0)   # 0x100000
BIG_STRIDE = 2 * SET_STRIDE  # 256KB — keeps bank bit unchanged

# ===== Trad-RH =====
trad_addrs = [base_a + i * BIG_STRIDE for i in range(9)]
trad_addrs += [base_b + i * BIG_STRIDE for i in range(8)]

# Make them unique (some overlap at row boundaries)
trad_addrs = list(dict.fromkeys(trad_addrs))  # remove dups while keeping order
while len(trad_addrs) < 17:
    trad_addrs.append(base_a + len(trad_addrs) * BIG_STRIDE)
trad_addrs = trad_addrs[:17]

print("=== Trad-RH ===")
for a in trad_addrs:
    d = decode(a)
    print(f"  0x{a:08X} -> set={llc_set(a)}, bank={d[1]}, row={d[2]}")
print(f"Unique: {len(set(trad_addrs))}, Same set: {len({llc_set(a) for a in trad_addrs})==1}")

with open("traces/trad_rh/trad_rh.trace", 'w') as f:
    for _ in range(500):
        for addr in trad_addrs:
            f.write(f"0x{addr:x}\n")

# ===== R2H =====
# To hit sets 0-255: use row bits to vary set index while keeping bank fixed
# Row bits start at bit 20. Set index uses bits [6:16].
# By varying row values, we shift bits into the set index range.
# Row increment of 1 shifts address by 1<<20 = 1MB, which changes set by (1MB>>6)&0x7FF = 0x4000&0x7FF = 0
# That doesn't work either. Let's try varying col within same row.
# col bits [6:15] directly map to set index bits [0:9]
# So col=0 gives set=0, col=1 gives set=1, ..., col=1023 gives various sets

r2h_addrs = []
for set_target in range(256):
    # col bits 0-9 overlap with set bits 0-9
    # To get set S: col = S (since set = (col<<0) & 0x3FF for lower 10 bits)
    # But set uses 11 bits [6:16], and col is only 10 bits [6:15]
    # Bit 16 of set comes from bank bit 0. We keep bank=0 so that bit is 0.
    # So sets 0-1023 are reachable via col alone (within same row+bank)
    col = set_target  # sets 0-255
    for way in range(8):
        r2h_addrs.append(base_a + (col << 6) + way * BIG_STRIDE)
    for way in range(8):
        r2h_addrs.append(base_b + (col << 6) + way * BIG_STRIDE)

print(f"\n=== R2H: {len(r2h_addrs)} addresses ===")
sets_found = sorted(set(llc_set(a) for a in r2h_addrs))
print(f"Sets covered: {len(sets_found)} (from {sets_found[0]} to {sets_found[-1]})")
for a in r2h_addrs[:8]:
    d = decode(a)
    print(f"  0x{a:08X} -> set={llc_set(a)}, bank={d[1]}, row={d[2]}")

with open("traces/r2h/r2h.trace", 'w') as f:
    for _ in range(100):
        for addr in r2h_addrs:
            f.write(f"0x{addr:x}\n")

print(f"\nDone! Traces written.")
