import sys, numpy as np
sys.path.insert(0,'/home/claude/marv/tools'); from lz import lz_decomp, lz_comp_opt as lz_comp
A0,AEND,B0,BEND=0x123951,0x1246de,0x1246de,0x12550e
def stream_to_raw(S):
    B=np.concatenate([S[:, i*128:(i+1)*128] for i in range(16)],axis=0)  # 256x128
    raw=bytearray()
    for t in range(512):
        r=(t//16)*8; c=(t%16)*8
        for y in range(8):
            p0=p1=0
            for x in range(8):
                v=int(B[r+y,c+x]); p0|=(v&1)<<(7-x); p1|=(v>>1)<<(7-x)
            raw+=bytes([p0,p1])
    return bytes(raw)
def insert(rom, S):
    raw=stream_to_raw(S); a=lz_comp(raw[:4096]); b=lz_comp(raw[4096:])
    assert len(a)<=AEND-A0 and len(b)<=BEND-B0,(len(a),len(b))
    rom[A0:A0+len(a)]=a; rom[B0:B0+len(b)]=b
    return len(a),len(b)
