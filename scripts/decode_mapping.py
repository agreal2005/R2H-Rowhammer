"""DRAM address mapping for DDR4_16Gb_x8 with RoBaRaCoCh.
Based on Ramulator2 source analysis:
  Levels: channel, rank, bankgroup, bank, row, column
  Org:    {1, 1, 4, 4, 131072, 1024}
  
RoBaRaCoCh consumes address bits (after 6-bit tx_offset) in order:
  rank(0), bg(2), bank(2), row(17) — then col(10) is taken from start
  Actually: col is taken FIRST from lsb, then rank,bg,bank,row sequentially
  
Key insight: row bits start at bit position (tx_offset + rank_bits + bg_bits + bank_bits)
           = 6 + 0 + 2 + 2 = 10
           row spans bits [10:26] (17 bits)
           
  bank bits: bits [8:9]  (2 bits)
  bg bits:   bits [6:7]  (2 bits)
  col bits:  bits [0:5] then row continues...
  
Wait — RoBaRaCoCh means Row-Bank-Rank-Column. Let me re-read...
Actually "RoBaRaCoCh" = Row, Bank, Rank, Column, Channel — but reversed?
The name suggests row bits are consumed first.
"""

TX_OFFSET = 6  # 64B blocks

def decode_robaracoch(addr):
    """RoBaRaCoCh: column first, then bank+group, then row at the top"""
    a = addr >> TX_OFFSET
    
    # Column: lowest 10 bits
    col = a & 0x3FF
    a >>= 10
    
    # Bank: next 2 bits
    bank = a & 0x3
    a >>= 2
    
    # Bankgroup: next 2 bits  
    bg = a & 0x3
    a >>= 2
    
    # Row: remaining bits (17 bits)
    row = a & 0x1FFFF
    
    return 0, bg, bank, row, col  # rank=0

# Test: find two addresses in same bank, adjacent rows
# Bank=0 means bits [10:11] = 0
# Row N: bits [14:] = N
# So address = (row << 14) | (bank << 10) | col, with col=0
def make_addr(row, bank=0, col=0):
    return ((row << 14) | (bank << 10) | col) << TX_OFFSET

addr1 = make_addr(row=0, bank=0)
addr2 = make_addr(row=1, bank=0)  # adjacent row!
addr3 = make_addr(row=2, bank=0)

r1, bg1, b1, row1, c1 = decode_robaracoch(addr1)
r2, bg2, b2, row2, c2 = decode_robaracoch(addr2)
r3, bg3, b3, row3, c3 = decode_robaracoch(addr3)

print(f"Addr 0x{addr1:X} -> bank={b1}, row={row1}")
print(f"Addr 0x{addr2:X} -> bank={b2}, row={row2}")
print(f"Addr 0x{addr3:X} -> bank={b3}, row={row3}")

# Verify: traditional Rowhammer — 17 addresses mapping to same LLC set
# LLC: 2048 sets, 16-way. Set index = (addr>>6) & 0x7FF
print("\n--- 17 addresses for set 0 ---")
for i in range(17):
    addr = i << 17  # each 128KB apart
    set_idx = (addr >> 6) & 0x7FF
    r, bg, b, row, c = decode_robaracoch(addr)
    print(f"  0x{addr:08X} -> set={set_idx}, bank={b}, row={row}")
