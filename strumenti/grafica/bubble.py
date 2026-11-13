import numpy as np
BASE=0x269800
def get_line(d,row):
    a=np.zeros((16,128),np.uint8)
    for half in (0,1):
        for c in range(16):
            t=row*32+half*16+c; o=BASE+t*16
            for y in range(8):
                for x in range(8):
                    a[half*8+y,c*8+x]=((d[o+2*y]>>(7-x))&1)|(((d[o+2*y+1]>>(7-x))&1)<<1)
    return a
def put_line(d,row,a):
    for half in (0,1):
        for c in range(16):
            t=row*32+half*16+c; o=BASE+t*16
            for y in range(8):
                p0=p1=0
                for x in range(8):
                    v=int(a[half*8+y,c*8+x]); p0|=(v&1)<<(7-x); p1|=(v>>1)<<(7-x)
                d[o+2*y]=p0; d[o+2*y+1]=p1
def segs(a,x0):
    m=(a==1).any(axis=0); out=[]; x=x0
    while x<128:
        if m[x]:
            s=x
            while x<128 and m[x]: x+=1
            out.append((s,x))
        else: x+=1
    return out

X10=lambda *r: list(r)
F={}
def g(ch, top, rows):   # top = prima riga (2 = maiuscole/ascendenti, 4 = minuscole)
    F[ch]=(top, rows)
g('a',4,[".####.","######","##..##","##..##","..####","###.##","##..##","##..##","######",".##.##"])
g('o',4,[".####.","######"]+["##..##"]*6+["######",".####."])
g('e',4,[".####.","######","##..##","##..##","######","######","##....","##..##","######",".####."])
g('c',4,[".####.","######","##..##","##....","##....","##....","##....","##..##","######",".####."])
g('n',4,["##.##.","######"]+["##..##"]*8)
g('u',4,["##..##"]*8+["######",".##.##"])
g('r',4,["##.##","#####"]+["##..."]*8)
g('i',2,["##","##",".."]+["##"]*9)
g('l',2,["##"]*12)
g('s',4,[".####.","######","##....","####..",".####.","..####","....##","##..##","######",".####."])
g('p',4,["##.##.","######"]+["##..##"]*6+["######","##.##.","##....","##...."])
g('q',4,[".##.##","######"]+["##..##"]*6+["######",".##.##","....##","....##"])
g('g',4,[".##.##","######"]+["##..##"]*6+["######",".##.##","....##",".####."])
g('d',2,["....##","....##",".##.##","######"]+["##..##"]*6+["######",".##.##"])
g('t',3,[".##..",".##..","#####","#####"]+[".##.."]*5+[".####","..###"])
g('v',4,["##..##"]*6+[".#..#.",".####.","..##..","..##.."])
g('z',4,["######","######","...##.","...##.","..##..","..##..",".##...",".##...","######","######"])
g('f',2,[".###",".###",".##.","####","####"]+[".##."]*7)
g('m',4,["##.##.##..","##########"]+["##..##..##"]*8)
g('h',2,["##....","##....","##.##.","######"]+["##..##"]*8)
g('M',2,["####.####"]*4+["##.#.#.##"]*2+["##.###.##"]*6)
g('P',2,["######.","#######","##...##","##...##","#######","######."]+["##....."]*6)
g('N',2,["###...##","####..##","####..##","##.##.##","##.##.##","##..####","##..####","##...###","##...###","##....##","##....##","##....##"])
g('H',2,["##...##"]*5+["#######"]*2+["##...##"]*5)
g('?',2,[".####.","######","##..##","...###","..###.","..##..","..##..","..##..","......","..##..","..##..","......"])
g(' ',4,["...."])
def width(text): return sum(len(F[c][1][0])+1 for c in text)-1
def draw(a, x, text):
    for ch in text:
        top, rows = F[ch]
        for k, r in enumerate(rows):
            for j, b in enumerate(r):
                if b=='#': a[top+k, x+j]=1
        x += len(rows[0])+1
    return x

# ---- menu Chiama / Esci (font con contorno)
OF={'C':(2,["ooo","o..","o..","o..","o..","o..","o..","o..","o..","o..","o..","ooo"]),
    'E':(2,["ooo","o..","o..","o..","o..","ooo","o..","o..","o..","o..","o..","ooo"]),
    'h':(2,["o..","o..","o..","o..","ooo","o.o","o.o","o.o","o.o","o.o","o.o","o.o"]),
    'i':(3,["o",".",".","o","o","o","o","o","o","o","o"]),
    'a':(6,["ooo","..o","ooo","o.o","o.o","o.o","o.o","ooo"]),
    'm':(6,["ooooo","o.o.o","o.o.o","o.o.o","o.o.o","o.o.o","o.o.o","o.o.o"]),
    's':(6,["ooo","o..","o..","ooo","..o","..o","..o","ooo"]),
    'c':(6,["ooo","o..","o..","o..","o..","o..","o..","ooo"])}
def draw_outlined(a, x0, x1, text):
    m=np.zeros((16,128),bool); x=x0+1
    for ch in text:
        top,rows=OF[ch]
        for k,r in enumerate(rows):
            for j,b in enumerate(r):
                if b=='o': m[top+k,x+j]=True
        x+=len(rows[0])+1
    assert x<=x1, (text,x,x1)
    a[:, x0:x1]=0
    o=np.zeros_like(m)
    for dy in (-1,0,1):
        for dx in (-1,0,1): o|=np.roll(np.roll(m,dy,0),dx,1)
    a[(o&~m)]=1; a[m]=2

def patch(rom):
    T={12:'per cercare',13:'in squadra',14:'per gli oggetti',15:'per uscire'}
    for r,t in T.items():
        a=get_line(rom,r); a[:,32:][a[:,32:]==1]=2; draw(a,32,t); put_line(rom,r,a)
    a=get_line(rom,16)                       # Muovi [mano] con [croce]
    for x0,x1 in ((0,40),(63,103)): reg=a[:,x0:x1]; reg[reg==1]=2
    draw(a,2,'Muovi'); draw(a,68,'con'); put_line(rom,16,a)
    a=get_line(rom,17); reg=a[:,0:86]; reg[reg==1]=2; draw(a,84-width('Premi'),'Premi'); put_line(rom,17,a)
    a=get_line(rom,18); a[a==1]=2; draw(a,(128-width('Non funziona'))//2,'Non funziona'); put_line(rom,18,a)
    a=get_line(rom,19); a[a==1]=2; draw(a,41,'Hmm?'); put_line(rom,19,a)
    a=get_line(rom,2); draw_outlined(a,15,40,'Chiama'); draw_outlined(a,40,64,'Esci'); put_line(rom,2,a)
