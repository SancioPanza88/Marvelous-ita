# Applica intro tradotta, glifi e crediti alla ROM compilata, poi rigenera il BPS.
import sys, numpy as np
sys.path.insert(0,'/home/claude/emu'); sys.path.insert(0,'/home/claude/marv/tools')
from intro_it import build; from streamio import insert; from glyphs_it import apply
from scene2_it import patch; import compila_m as C
rom_p, jp_p, bps_p = sys.argv[1:4]
rom=bytearray(open(rom_p,'rb').read())
S=apply(build(np.load('/home/claude/emu/stream.npy')))
print('intro', insert(rom,S)); print('scena2', patch(rom))
C.fix_checksum(rom)
open(rom_p,'wb').write(rom)
open(bps_p,'wb').write(C.make_bps(open(jp_p,'rb').read(), bytes(rom)))
