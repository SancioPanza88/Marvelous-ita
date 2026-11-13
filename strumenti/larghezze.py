# Mostra la larghezza in pixel di ogni riga delle voci indicate ("!!" = troppo lunga).
# uso: python3 larghezze.py rom_tradotta.sfc copione_it.txt NNNN [NNNN ...]
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marv as M, compila_m as C
d = bytearray(open(sys.argv[1], 'rb').read())
W = M.widths(d); s = C.parse_script(sys.argv[2])
for n in sys.argv[3:]:
    toks = C.tokenize(int(n), s[int(n)], M.IT_TABLE, [])
    px = 0; txt = ''
    for k, v in toks + [('k', b'\xfb')]:
        if k == 'c': px += W.get(v, 12); txt += M.IT_TABLE.get(v, '?')
        elif v[:2] == b'\xfe\x6d': px += C.INLINE_PX.get(v[2], 16); txt += '@'
        elif v[0] == 0xFC: px += W.get(v[1], 12); txt += ':'
        elif v[0] in (0xF6, 0xF8, 0xF9, 0xFA, 0xFB) or v[:2] == b'\xfe\x69':
            if txt or px: print(n, '%3d%s %s' % (px, ' !!' if px > M.MAX_PX else '   ', txt))
            px = 0; txt = ''
