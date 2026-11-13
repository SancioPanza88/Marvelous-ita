# Icone nei dialoghi: EXIT -> ESCI, TEAM WORK -> SQUA/DRA (2bpp, non compresse)
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
SM={'S':["22222","22...","22222","...22","...22","22222"],'Q':["22222","22.22","22.22","22.22","22222","..222"],
    'U':["22.22"]*5+["22222"],'A':["22222","22.22","22222","22.22","22.22","22.22"],
    'D':["2222.","22.22","22.22","22.22","22.22","2222."],'R':["2222.","22.22","2222.","22.22","22.22","22.22"]}
def _draw(a,font,word,y0,x0,x1,gap=1):
    w=sum(len(font[c][0])+gap for c in word)-gap; x=x0+((x1-x0+1)-w)//2
    for c in word:
        for k,r in enumerate(font[c]):
            for j,b in enumerate(r):
                if b=='2': a[y0+k][x+j]=2
        x+=len(font[c][0])+gap
def patch(e):
    base,col,row=0x26c800,4,0                       # EXIT
    a=_get(e,base,col,row); assert a[0][0]==1 and a[2][5]==3
    for y in range(4,13):
        for x in range(4,28): a[y][x]=1
    _draw(a,BIG,'ESCI',4,4,27,gap=2); _put(e,base,col,row,a)
    base,col,row=0x26dc00,12,10                     # TEAM WORK
    a=_get(e,base,col,row)
    for y in range(1,15):
        for x in range(1,31): a[y][x]=1
    _draw(a,SM,'SQUA',1,1,30); _draw(a,SM,'DRA',9,1,30); _put(e,base,col,row,a)
