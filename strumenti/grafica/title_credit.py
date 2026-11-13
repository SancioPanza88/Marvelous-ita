import numpy as np
F={'2':["110","001","010","100","111"],'6':["011","100","110","101","010"],
   'S':["011","100","010","001","110"],'a':["000","011","101","101","011"],
   'n':["000","110","101","101","101"],'c':["000","011","100","100","011"],
   'i':["1","0","1","1","1"],'o':["000","010","101","101","010"],
   'p':["000","110","101","110","100"],'z':["000","111","001","010","111"],
   '8':["010","101","010","101","010"],' ':["0","0","0","0","0"]}
def make(text, cred):
    # © copiato dalla seconda riga dei crediti (colonne 17-25)
    L2=cred[1]; cop=cred[0][:, 17:23].copy(); cop[:,5]=np.where(cop[:,5]!=0,6,0)
    mask=np.zeros((8,120),bool); x=0; segs=[]
    out=np.zeros((8,120),int); out[:, :cop.shape[1]]=cop; x=cop.shape[1]
    for ch in text:
        g=F[ch]; w=len(g[0])
        for y,row in enumerate(g):
            for k,b in enumerate(row):
                if b=='1':
                    mask[1+y,x+k]=True
                    if ch=='p' and y==4: mask[6,x+k]=True
        x+=w+(2 if ch!=' ' else 1)
    W=x+1
    for y in range(8):
        for xx in range(W):
            if mask[y,xx]: out[y,xx]=0xC
            elif out[y,xx]==0 and any(mask[yy,xc] for yy in range(max(0,y-1),min(8,y+2)) for xc in range(max(0,xx-1),xx+2)):
                out[y,xx]=6
    return out[:, :W]

import sys
sys.path.insert(0,'/home/claude/marv/tools'); from lz import lz_decomp, lz_comp_opt
TS, TEND = 0x1d9481, 0x1da5ed
BLOCKS=[0x8c,0x8e,0xa8,0xaa,0xac,0xae]
def put4(buf, off, a):
    for y in range(8):
        for p in range(4):
            v=0
            for x in range(8): v|=((int(a[y,x])>>p)&1)<<(7-x)
            buf[off+(p//2)*16+2*y+(p%2)]=v
def patch_title(rom, cred):
    line=make('26 Sanciopanza88',cred); W=line.shape[1]
    m=line.copy(); m[(line!=0)&(line!=6)]=0xE; line=m   # 0xE e' bianco come 0xC, comprime meglio
    strip=np.zeros((8,96),int); x0=(96-W)//2; strip[:, x0:x0+W]=line
    o,l=lz_decomp(rom,TS,True); o=bytearray(o)
    for k,t in enumerate(BLOCKS):
        put4(o,0x800+t*32,strip[:, k*16:k*16+8]); put4(o,0x800+(t+1)*32,strip[:, k*16+8:k*16+16])
    c=lz_comp_opt(bytes(o)); assert len(c)<=TEND-TS,len(c)
    rom[TS:TS+len(c)]=c; rom[TS+len(c):TEND]=b'\xff'*(TEND-TS-len(c)) if False else rom[TS+len(c):TEND]
    # tabella sprite: 17 voci originali + 6 nuove, in spazio libero
    old=bytes(rom[0x2fff25:0x2fff69]); assert old[:4]==bytes([0x50,0xc0,0x80,0x20])
    new=old+b''.join(bytes([0x50+16*k,0xd0,t,0x20]) for k,t in enumerate(BLOCKS))
    assert all(b==0xff for b in rom[0x2fff9c:0x2fff9c+len(new)])
    rom[0x2fff9c:0x2fff9c+len(new)]=new
    code=bytes.fromhex('daa24000a940001869 2c00a8bd25ff990065bd27ff'.replace(' ',''))
    assert rom[0x2fff69:0x2fff69+len(code)]==code
    n=len(new)-4
    rom[0x2fff6a:0x2fff6d]=bytes([0xa2,n,0]); rom[0x2fff6d:0x2fff70]=bytes([0xa9,n,0])
    rom[0x2fff75:0x2fff78]=bytes([0xbd,0x9c,0xff]); rom[0x2fff7b:0x2fff7e]=bytes([0xbd,0x9e,0xff])
    return len(c)
