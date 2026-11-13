# Cartelli del menu (?!, TEAM WORK, ITEM, EXIT) -> SQUA/DRA, ROBA, ESCI
import numpy as np
BASE=0x2b6000; NT=0x1800//32
F7={'E':["####","##..","##..","####","##..","##..","####"],'S':["####","##..","##..","####","..##","..##","####"],
    'C':["####","##..","##..","##..","##..","##..","####"],'I':["##"]*7,
    'Q':["#####","##.##","##.##","##.##","##.##","#####","..###"],'U':["##.##"]*6+["#####"],
    'A':["#####","##.##","##.##","#####","##.##","##.##","##.##"],'D':["####.","##.##","##.##","##.##","##.##","##.##","####."],
    'R':["####.","##.##","##.##","####.","##.##","##.##","##.##"],'O':["#####"]+["##.##"]*5+["#####"],
    'B':["####.","##.##","##.##","####.","##.##","##.##","####."]}
def load(rom):
    A=np.zeros((96,128),int)
    for t in range(NT):
        o=BASE+t*32
        for y in range(8):
            for x in range(8):
                A[(t//16)*8+y,(t%16)*8+x]=sum(((rom[o+(p//2)*16+2*y+(p%2)]>>(7-x))&1)<<p for p in range(4))
    return A
def store(rom,A):
    for t in range(NT):
        o=BASE+t*32
        for y in range(8):
            for p in range(4):
                v=0
                for x in range(8): v|=((int(A[(t//16)*8+y,(t%16)*8+x])>>p)&1)<<(7-x)
                rom[o+(p//2)*16+2*y+(p%2)]=v
def get(A,pair,band): return np.vstack([A[band:band+16,pair*32:pair*32+32],A[band:band+16,(pair+1)*32:(pair+1)*32+32]])
def put(A,pair,band,s,rows=32):
    A[band:band+16,pair*32:pair*32+32]=s[:16]
    if rows>16: A[band:band+16,(pair+1)*32:(pair+1)*32+32]=s[16:32]
def text(s,word,x0,y0,T,O,scale=1,outline=True,x1=None):
    w=sum(len(F7[c][0])+1 for c in word)-1
    if x1 is not None: x0=x0+((x1-x0+1)-w)//2
    m=np.zeros_like(s,bool); x=x0
    for c in word:
        g=F7[c]
        for r,row in enumerate(g):
            for k,b in enumerate(row):
                if b=='#':
                    for dy in range(scale): m[y0+r*scale+dy,x+k]=True
        x+=len(g[0])+1
    if outline:
        o=np.zeros_like(m)
        for dy in (-1,0,1):
            for dx in (-1,0,1): o|=np.roll(np.roll(m,dy,0),dx,1)
        s[o&~m]=O
    s[m]=T
def patch(rom):
    A=load(rom)
    for pair,band,dark in ((2,0,True),(2,64,False)):           # TEAM WORK -> SQUA DRA
        s=get(A,pair,band); clean=s[4].copy()
        for y in range(5,24): s[y]=clean
        T,O=(2,0xD) if dark else (0xE,9)
        text(s,'SQUA',7,7,T,O,x1=30); text(s,'DRA',7,16,T,O,x1=30)
        put(A,pair,band,s)
    for pair,band,dark in ((2,48,True),(2,80,False)):          # EXIT -> ESCI
        s=get(A,pair,band); clean=s[4].copy(); clean[9:29]=0xD if dark else 9
        for y in range(5,12): s[y]=clean
        text(s,'ESCI',9,5,2 if dark else 0xE,0,outline=False,x1=28)
        put(A,pair,band,s,rows=16)
    store(rom,A)
