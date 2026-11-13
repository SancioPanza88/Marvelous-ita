# Compila la traduzione italiana di Marvelous.
# uso: python3 compila_m.py rom_inglese.sfc copione_it.txt rom_giapponese.sfc cartella_output [--en]
import sys, os, re, struct, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marv as M

# ---------------------------------------------------------------- lettere accentate
GRAVE = ['..####..........', '..##++##........', '....##++##......', '......####......']
ACUTE = ['......####......', '....##++##......', '..##++##........', '..####..........']
ACCENTS = {0x53: (0x28, GRAVE), 0x54: (0x2C, GRAVE), 0x55: (0x2C, ACUTE),
           0x56: (0x30, GRAVE), 0x57: (0x36, GRAVE), 0x58: (0x3C, GRAVE)}

def make_accents(d):
    code = {'.': 0, '#': 1, '+': 2}
    for slot, (base, acc) in ACCENTS.items():
        g = M.glyph_rows(d, base)
        if base == 0x30:                       # i: togli il puntino (righe 0-3)
            for y in range(0, 4): g[y] = [0] * 16
            acc = ['####............', '##++##..........', '..##++##........', '....####........']
        for y, row in enumerate(acc):
            for x, ch in enumerate(row):
                if ch != '.': g[y][x] = code[ch]
        M.put_glyph(d, slot, g)

# ---------------------------------------------------------------- copione
SUBST = {'È': "E'", 'À': "A'", 'Ì': "I'", 'Ò': "O'", 'Ù': "U'", '’': "'", '‘': "'", '“': '"', '”': '"', '...': '…'}
TOKEN = re.compile(r'<P>|<[0-9A-Fa-f ]+>|[123]\||\{[0-9A-Fa-f]{2}\}|.', re.S)

def parse_script(path):
    entries = {}; cur = None; buf = []
    for raw in open(path, encoding='utf-8').read().split('\n'):
        if raw.startswith('###'):
            if cur is not None: entries[cur] = ''.join(buf)
            cur = int(raw.split()[1]); buf = []
        elif raw.startswith(';') or raw.startswith('#') or cur is None:
            continue
        else:
            buf.append(raw.rstrip('\r'))
    if cur is not None: entries[cur] = ''.join(buf)
    return entries

def tokenize(n, text, table, warn):
    for a, b in SUBST.items(): text = text.replace(a, b)
    rev = {}
    for k, v in table.items():
        if len(v) == 1: rev.setdefault(v, k)
    multi = sorted((v for v in table.values() if len(v) > 1 and not v.startswith('{')), key=len, reverse=True)
    pat = TOKEN if not multi else re.compile('|'.join(re.escape(x) for x in multi) + '|' + TOKEN.pattern, re.S)
    for v in multi: rev[v] = [k for k, x in table.items() if x == v][0]
    toks = []
    for m in pat.finditer(text):
        t = m.group()
        if t == '<P>': toks.append(('k', b'\xfe\x69'))
        elif t.startswith('<'): toks.append(('k', bytes(int(x, 16) for x in t[1:-1].split())))
        elif t in ('1|', '2|', '3|'): toks.append(('k', bytes([{'1': 0xF6, '2': 0xF8, '3': 0xF9}[t[0]]])))
        elif t.startswith('{'): toks.append(('c', int(t[1:3], 16)))
        elif t in rev: toks.append(('c', rev[t]))
        else:
            warn.append('%04d: carattere non disponibile %r' % (n, t)); toks.append(('c', 0xF0))
    return toks

def encode(toks):
    out = bytearray()
    for kind, v in toks:
        if kind == 'c': out.append(v)
        else: out += v
    return bytes(out)

INLINE_PX = {0x1A: 48}      # FE 6D 1A = nome della squadra (stima)
def check_lines(n, toks, W, warn):
    px = 0
    for kind, v in toks + [('k', b'\xfb')]:
        if kind == 'c':
            px += W.get(v, 12)
        elif v[:2] == b'\xfe\x6d':
            px += INLINE_PX.get(v[2], 16)
        elif v[0] == 0xFC:
            px += W.get(v[1], 12)
        elif v[0] in (0xF6, 0xF8, 0xF9, 0xFA, 0xFB) or v[:2] == b'\xfe\x69':
            if px > M.MAX_PX:
                warn.append('%04d: riga troppo lunga (%d/%d)' % (n, px, M.MAX_PX))
            px = 0

def ctrl_seq(toks):
    return [v for k, v in toks if k == 'k']

# ---------------------------------------------------------------- checksum / patch
def fix_checksum(d):
    d[0x7FDC:0x7FE0] = b'\xff\xff\x00\x00'
    s = sum(d) & 0xFFFF
    struct.pack_into('<HH', d, 0x7FDC, s ^ 0xFFFF, s)

def _vlq(n):
    out = bytearray()
    while True:
        x = n & 0x7F; n >>= 7
        if n == 0:
            out.append(0x80 | x); return bytes(out)
        out.append(x); n -= 1

def make_bps(src, dst):
    out = bytearray(b'BPS1') + _vlq(len(src)) + _vlq(len(dst)) + _vlq(0)
    i = 0; n = len(dst)
    while i < n:
        same = i < len(src) and src[i] == dst[i]
        j = i
        while j < n and (j < len(src) and src[j] == dst[j]) == same: j += 1
        out += _vlq(((j - i - 1) << 2) | (0 if same else 1))
        if not same: out += dst[i:j]
        i = j
    out += struct.pack('<II', zlib.crc32(src) & 0xFFFFFFFF, zlib.crc32(dst) & 0xFFFFFFFF)
    out += struct.pack('<I', zlib.crc32(out) & 0xFFFFFFFF)
    return bytes(out)

# ---------------------------------------------------------------- main
def main(en_path, script_path, jp_path, outdir, en_mode=False):
    d = bytearray(open(en_path, 'rb').read())
    jp = open(jp_path, 'rb').read()
    orig, old_end = M.parse(d)
    table = M.EN_TABLE if en_mode else M.IT_TABLE
    if not en_mode: make_accents(d)
    W = M.widths(d)
    script = parse_script(script_path)
    if sorted(script) != list(range(len(orig))):
        raise SystemExit('ERRORE: il copione deve avere le voci 0000-%04d' % (len(orig) - 1))
    warn = []; blob = bytearray()
    for n in range(len(orig)):
        toks = tokenize(n, script[n], table, warn)
        if ctrl_seq(toks) != ctrl_seq(orig[n]):
            warn.append('%04d: codici diversi dall\'originale' % n)
        check_lines(n, toks, W, warn)
        blob += encode(toks)
    blob.append(0xFF)
    if M.SCRIPT_START + len(blob) > M.SCRIPT_LIMIT: raise SystemExit('ERRORE: copione troppo grande')
    clear_end = max(old_end + 1, M.SCRIPT_START + len(blob))
    d[M.SCRIPT_START:clear_end] = b'\xff' * (clear_end - M.SCRIPT_START)
    d[M.SCRIPT_START:M.SCRIPT_START + len(blob)] = blob
    # verifica: il gioco deve ritrovare lo stesso numero di voci
    chk, _ = M.parse(d)
    if len(chk) != len(orig): raise SystemExit('ERRORE: numero di voci cambiato (%d)' % len(chk))
    fix_checksum(d)
    os.makedirs(outdir, exist_ok=True)
    rom = os.path.join(outdir, 'Marvelous - Another Treasure Island (ITA).sfc')
    open(rom, 'wb').write(d)
    open(os.path.join(outdir, 'marvelous_ita.bps'), 'wb').write(make_bps(jp, bytes(d)))
    print('copione: %d byte (%d liberi)' % (len(blob), M.SCRIPT_LIMIT - M.SCRIPT_START - len(blob)))
    print('CRC32 ROM: %08X' % (zlib.crc32(d) & 0xFFFFFFFF))
    if warn:
        print('%d avvisi' % len(warn))
        for w in warn[:300]: print('  ' + w)
    return d

if __name__ == '__main__':
    a = sys.argv[1:]
    en_mode = '--en' in a
    a = [x for x in a if x != '--en']
    main(a[0], a[1], a[2], a[3], en_mode)
