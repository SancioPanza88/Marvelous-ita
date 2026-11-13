# LIFE -> VITA nella schermata della squadra (2 tile 2bpp, non compresse)
BASE = 0x268000 + 11 * 16
G = {'V': ["2.2"] * 5 + [".2."], 'I': ["2"] * 6, 'T': ["222"] + [".2."] * 5,
     'A': [".2.", "2.2", "222", "2.2", "2.2", "2.2"]}
def patch(e):
    m = [[0] * 16 for _ in range(8)]; x = 1
    for ch in 'VITA':
        for k, r in enumerate(G[ch]):
            for j, b in enumerate(r):
                if b == '2': m[1 + k][x + j] = 1
        x += len(G[ch][0]) + 1
    px = [[0] * 16 for _ in range(8)]
    for y in range(8):
        for xx in range(16):
            if m[y][xx]: px[y][xx] = 2
            elif any(m[yy][xc] for yy in range(max(0, y - 1), min(8, y + 2)) for xc in range(max(0, xx - 1), min(16, xx + 2))):
                px[y][xx] = 1
    for t in range(2):
        o = BASE + t * 16
        for y in range(8):
            p0 = p1 = 0
            for k in range(8):
                v = px[y][t * 8 + k]; p0 |= (v & 1) << (7 - k); p1 |= (v >> 1) << (7 - k)
            e[o + 2 * y] = p0; e[o + 2 * y + 1] = p1
