# Icone nei dialoghi: EXIT -> ESCI, TEAM WORK -> SQUA/DRA, nello stile di ITEM e ?! (2bpp, non compresse)
def _get(e,base,col,row):
    a=[[0]*32 for _ in range(16)]
    for half in (0,1):
        for c in range(4):
            o=base+((row+half)*16+col+c)*16
            for y in range(8):
                for x in range(8):
                    a[half*8+y][c*8+x]=((e[o+2*y]>>(7-x))&1)|(((e[o+2*y+1]>>(7-x))&1)<<1)
    return a
def _put(e,base,col,row,a):
    for half in (0,1):
        for c in range(4):
            o=base+((row+half)*16+col+c)*16
            for y in range(8):
                p0=p1=0
                for x in range(8):
                    v=a[half*8+y][c*8+x]; p0|=(v&1)<<(7-x); p1|=(v>>1)<<(7-x)
                e[o+2*y]=p0; e[o+2*y+1]=p1
BIG={'E':["2222","22..","22..","22..","222.","22..","22..","22..","2222"],
     'S':[".222","22..","22..","22..",".22.","..22","..22","..22","222."],
     'C':[".222"]+["22.."]*7+[".222"],'I':["22"]*9}
SM={'S':["22222","22...","22222","...22","22222"],'Q':["22222","22.22","22.22","22222","..222"],
    'U':["22.22"]*4+["22222"],'A':["22222","22.22","22222","22.22","22.22"],
    'D':["2222.","22.22","22.22","22.22","2222."],'R':["2222.","22.22","2222.","22.22","22.22"]}
def _blank():
    a=[[3]*32 for _ in range(16)]
    for x in range(32): a[0][x]=a[15][x]=1
    for y in range(16): a[y][0]=a[y][31]=1
    for x in range(1,31): a[1][x]=2
    return a
def _draw(a,font,word,y0,gap=2):
    w=sum(len(font[c][0])+gap for c in word)-gap; x=1+(30-w)//2
    m=[[False]*32 for _ in range(16)]
    for c in word:
        for k,r in enumerate(font[c]):
            for j,b in enumerate(r):
                if b=='2': m[y0+k][x+j]=True
        x+=len(font[c][0])+gap
    for y in range(2,15):
        for xx in range(1,31):
            if m[y][xx]: a[y][xx]=2
            elif any(m[yy][xc] for yy in (y-1,y,y+1) for xc in (xx-1,xx,xx+1) if 0<=yy<16 and 0<=xc<32): a[y][xx]=1
def patch(e):
    a=_blank(); _draw(a,BIG,'ESCI',4); _put(e,0x26c800,4,0,a)
    a=_blank(); _draw(a,SM,'SQUA',3); _draw(a,SM,'DRA',9); _put(e,0x26dc00,12,10,a)
