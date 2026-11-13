# Anteprima dei testi: disegna le pagine di alcune voci col font della ROM tradotta.
# uso: python3 anteprima_m.py rom.sfc copione.txt out.png NNNN [NNNN ...]
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marv as M, compila_m as C
from PIL import Image, ImageDraw

rom, scr, out = sys.argv[1:4]
ids = [int(x) for x in sys.argv[4:]]
d = bytearray(open(rom, 'rb').read())
W = M.widths(d)
s = C.parse_script(scr)
PAL = [(24, 32, 80), (250, 250, 250), (120, 120, 160), (200, 200, 220)]

pages = []
for n in ids:
    toks = C.tokenize(n, s[n], M.IT_TABLE, [])
    page = [[]]
    for k, v in toks:
        if k == 'c':
            page[-1].append(v)
        elif v[0] in (0xF6, 0xF8, 0xF9):
            if page[-1]: page.append([])
        elif v[:2] == b'\xfe\x69' or v[0] in (0xFA, 0xFB):
            pages.append((n, page)); page = [[]]
        elif v[:2] == b'\xfe\x6d':
            page[-1].append('@')
        elif v[0] == 0xFC:
            page[-1].append(v[1])
    if any(page): pages.append((n, page))

LH, PADX, PADY = 16, 8, 6
BW, BH = 256 + 2 * PADX, 3 * LH + 2 * PADY
img = Image.new('RGB', (BW * 2, (BH + 14) * ((len(pages) + 1) // 2)), (0, 0, 0))
dr = ImageDraw.Draw(img)
for i, (n, page) in enumerate(pages):
    ox, oy = (i % 2) * BW, (i // 2) * (BH + 14)
    dr.rectangle([ox, oy + 12, ox + BW - 2, oy + 12 + BH], fill=PAL[0])
    dr.text((ox + 2, oy), '%04d' % n, fill=(255, 220, 0))
    for li, line in enumerate(page[:3]):
        x = ox + PADX; y = oy + 12 + PADY + li * LH
        for c in line:
            if c == '@':
                dr.rectangle([x, y + 3, x + 14, y + 12], outline=(255, 120, 120)); x += 16; continue
            if c in (0xF0, 0xF1):
                x += M.SPACE_PX; continue
            g = M.glyph_rows(d, c)
            for yy in range(16):
                for xx in range(16):
                    if g[yy][xx]: img.putpixel((x + xx, y + yy), PAL[g[yy][xx]])
            x += W.get(c, 12)
img = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
img.save(out)
print(out, len(pages), 'pagine')
