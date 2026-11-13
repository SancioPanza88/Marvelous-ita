# Marvelous: Another Treasure Island - libreria per la traduzione italiana
# Base: traduzione inglese di Tashi + DackR v1.07 (+ FastROM di Kandowontu)
# Il copione e' un blocco unico a 0x300000 ($F0:0000). All'avvio il gioco lo scorre
# e indicizza una voce dopo ogni FB/FA: numero e ordine delle voci vanno preservati.
import struct

SCRIPT_START = 0x300000
SCRIPT_LIMIT = 0x3F0000          # spazio disponibile (la ROM inglese e' 4 MB, vuota dopo 0x332BC3)
LEN_TABLE = 0x7B5E               # $00:FB5E lunghezza codici F2..FF
FE_TABLE = 0x7BFB                # $00:FBFB argomenti extra dei comandi FE xx
FONT = 0x2AC000                  # 64 byte per carattere (16x16, 2bpp, TL BL TR BR)
MAX_PX = 256                     # larghezza massima riga (unita' = pixel del font)
SPACE_PX = 8

def base_table():
    t = {}
    for i in range(26):
        t[i] = chr(65 + i); t[0x28 + i] = chr(97 + i)
    for i in range(10): t[0x1E + i] = str(i)
    t.update({0xF0: ' ', 0x42: '&', 0x43: '-', 0x44: '$', 0x45: '*', 0x46: '?', 0x47: '!', 0x48: '…',
              0x49: ',', 0x4A: '.', 0x4B: "'", 0x4C: '~', 0x4D: '"', 0x4E: '#', 0x4F: '♪'})
    return t

EN_TABLE = base_table()
EN_TABLE.update({0x53: "'r", 0x54: "'s", 0x55: "'v", 0x56: "'m", 0x57: "'d", 0x58: "'l", 0x59: "'t"})
IT_TABLE = base_table()
IT_TABLE.update({0x53: 'à', 0x54: 'è', 0x55: 'é', 0x56: 'ì', 0x57: 'ò', 0x58: 'ù'})

LINE_CODES = {0xF6: '1|', 0xF8: '2|', 0xF9: '3|'}

def tables(d):
    return d[LEN_TABLE:LEN_TABLE + 0x100], d[FE_TABLE:FE_TABLE + 0x100]

def parse(d):
    """Restituisce lista di voci; ogni voce = lista di token (('c',b) | ('k',bytes))."""
    L, F = tables(d)
    i = SCRIPT_START; entries = [[]]
    while True:
        b = d[i]
        if b == 0xFF: break
        if b < 0xF2:
            entries[-1].append(('c', b)); i += 1; continue
        n = 1 + F[d[i + 1]] if b == 0xFE else L[b]
        entries[-1].append(('k', bytes(d[i:i + n]))); i += n
        if b in (0xFB, 0xFA): entries.append([])
    return entries, i

def toks_to_text(toks, table):
    out = []
    for kind, v in toks:
        if kind == 'c':
            out.append(table.get(v, '{%02X}' % v))
        else:
            b = v[0]
            if b in LINE_CODES: out.append('\n' + LINE_CODES[b])
            elif v == b'\xfe\x69': out.append('<P>')
            else: out.append('<' + ' '.join('%02X' % x for x in v) + '>')
    return ''.join(out)

def glyph_rows(d, c):
    def tile(o):
        return [[((d[o + 2 * y] >> (7 - x)) & 1) | (((d[o + 2 * y + 1] >> (7 - x)) & 1) << 1) for x in range(8)] for y in range(8)]
    o = FONT + c * 64; g = [[0] * 16 for _ in range(16)]
    for k, (dx, dy) in enumerate(((0, 0), (0, 8), (8, 0), (8, 8))):
        t = tile(o + k * 16)
        for y in range(8):
            for x in range(8): g[dy + y][dx + x] = t[y][x]
    return g

def put_glyph(d, c, g):
    o = FONT + c * 64
    for k, (dx, dy) in enumerate(((0, 0), (0, 8), (8, 0), (8, 8))):
        for y in range(8):
            p0 = p1 = 0
            for x in range(8):
                v = g[dy + y][dx + x]
                p0 |= (v & 1) << (7 - x); p1 |= (v >> 1) << (7 - x)
            d[o + k * 16 + 2 * y] = p0; d[o + k * 16 + 2 * y + 1] = p1

def widths(d):
    W = {}
    for c in range(0xF0):
        g = glyph_rows(d, c)
        cols = [x for x in range(16) if any(g[y][x] for y in range(16))]
        W[c] = (max(cols) + 1) if cols else 0
    W[0xF0] = W[0xF1] = SPACE_PX
    return W
