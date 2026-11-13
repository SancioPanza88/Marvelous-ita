# Parole del font sottile (salvataggi, nome squadra, capitoli) in italiano
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marv as M
X = '2'
LO = {  # righe 5-12 (+13-14 per le discendenti)
 'a':["222","..2","222","2.2","2.2","2.2","2.2","222"], 'c':["222"]+["2.."]*6+["222"],
 'e':["222","2.2","2.2","222","2..","2..","2.2","222"], 'g':["222"]+["2.2"]*6+["222","..2","222"],
 'i':None, 'l':None, 'n':["222"]+["2.2"]*7, 'o':["222"]+["2.2"]*6+["222"],
 'p':["222"]+["2.2"]*6+["222","2..","2.."], 'q':["222"]+["2.2"]*6+["222","..2","..2"],
 'r':["222"]+["2.."]*7, 's':["222","2..","2..","222","..2","..2","..2","222"],
 'u':["2.2"]*7+["222"], 'v':["2.2"]*7+[".2."], 'z':["222","..2","..2",".2.",".2.","2..","2..","222"],
 'd':None, 't':None, 'b':None, 'h':None, 'm':["22222"]+["2.2.2"]*7,
}
UP = {  # righe 2-12
 'S':["222","2..","2..","2..","222","..2","..2","..2","..2","..2","222"],
 'N':["2..2","22.2","22.2","2.22","2.22"]+["2..2"]*6, 'P':["222","2.2","2.2","2.2","222"]+["2.."]*6,
 'I':["2"]*11, 'A':["222"]+["2.2"]*3+["222"]+["2.2"]*6, 'C':["222"]+["2.."]*9+["222"],
 'L':["2.."]*10+["222"], 'M':["2...2","22.22","2.2.2","2.2.2"]+["2...2"]*7,
 'R':["222","2.2","2.2","2.2","222","22.","2.2","2.2","2.2","2.2","2.2"],
 'B':["22.","2.2","2.2","2.2","22."]+["2.2"]*5+["22."], 'G':["222","2..","2..","2..","2..","2.2","2.2","2.2","2.2","2.2","222"],
 'R':["222","2.2","2.2","2.2","222","22.","2.2","2.2","2.2","2.2","2.2"],
}
def glyph(ch):
    if ch in UP: return 2, UP[ch]
    if ch == 'i': return 3, ["2", ".", "2", "2", "2", "2", "2", "2", "2", "2"]
    if ch == 'l': return 2, ["2"] * 11
    if ch == 't': return 3, [".2.", ".2.", "222"] + [".2."] * 6 + [".22"]
    if ch == 'd': return 2, ["..2", "..2", "..2", "222"] + ["2.2"] * 6 + ["222"]
    if ch == 'h': return 2, ["2..", "2..", "2..", "222"] + ["2.2"] * 7
    if ch == 'b': return 2, ["2..", "2..", "2..", "222"] + ["2.2"] * 6 + ["222"]
    if ch == '.': return 12, ["2"]
    if ch == ' ': return 12, [".."]
    return 5, LO[ch]
def render(text, W):
    m = [[0] * (W + 4) for _ in range(16)]; x = 1
    for ch in text:
        top, rows = glyph(ch)
        for k, r in enumerate(rows):
            for j, b in enumerate(r):
                if b == '2': m[top + k][x + j] = 1
        x += len(rows[0]) + 1
    used = x
    out = [[0] * W for _ in range(16)]
    for y in range(16):
        for xx in range(W):
            if m[y][xx]: out[y][xx] = 2
            elif any(m[yy][xc] for yy in range(max(0, y - 1), min(16, y + 2)) for xc in range(max(0, xx - 1), xx + 2)):
                out[y][xx] = 1
    return out, used
PHRASES = [  # (codici, testo)
    ([0x50, 0x51, 0x52], 'Squadra'), ([0x5B], 'Cap'), ([0x5C, 0x5D, 0x5E, 0x5F], 'Nuova partita'),
    (list(range(0x60, 0x67)), 'Campo estivo'), (list(range(0x67, 0x6E)), 'Il pirata Benson'),
    (list(range(0x6E, 0x74)), 'Il Baobab'), (list(range(0x74, 0x7A)), 'Regno di Lilliput'),
    (list(range(0x7A, 0x7E)), 'Maestra Gina...'), ([0x7F, 0x80], 'Muovi'), ([0x81, 0x82], 'Scegli'),
    ([0x83, 0x84, 0x85], 'Avanti'), ([0x86, 0x87, 0x88], 'Indietro'), ([0x89, 0x8A], 'Canc.'),
    ([0x8B, 0x8C], 'Inizia'), ([0x91, 0x92], 'Salva'),
]
def patch(d, check_only=False):
    W = M.widths(d); rep = []
    for codes, text in PHRASES:
        tot = sum(W[c] for c in codes)
        strip, used = render(text, tot + 16)
        rep.append((text, used, tot))
        if used > tot: raise SystemExit('troppo lungo: %s %d/%d' % (text, used, tot))
        if check_only: continue
        x0 = 0; x = 0
        for c in codes:
            rows = [[0] * 16 for _ in range(16)]
            for y in range(16):
                for k in range(W[c]):
                    sx = x + k - x0
                    if 0 <= sx < used: rows[y][k] = strip[y][sx]
            M.put_glyph(d, c, rows); x += W[c]
    return rep
