import sys,struct; sys.path.insert(0,'/home/claude/marv/tools'); from lz import lz_decomp, lz_comp_opt as lz_comp
MAP0, MAPEND = 0x21b9ac, 0x21bbd0
L='ABCDEFGHI8ZLMNOP-RSTUVW:Y,.'
def ent(ch):
    if ch==' ': return 0x22a
    col=202+2*L.index(ch); return 0x2000|((col//16)*32+col%16)
TOP=[(0,'-OGGI-'),(4,'UN CAMPEGGIO'),(6,'PER GIOVANI SI'),(8,'TIENE SU UNA'),(10,'ISOLA LONTANA.'),(14,'INTANTO...'),
     (23,'UNA BANDA DI'),(25,'PIRATI SBARCA'),(27,'SULLA STESSA'),(29,'ISOLA PER'),(31,'CERCARE IL')]
def put(w,half,row,c0,text):
    for c in range(16): w[half*1024+row*32+c0+c]=0x22a
    s=(16-len(text))//2
    for k,ch in enumerate(text): w[half*1024+row*32+c0+s+k]=ent(ch)
def patch(rom):
    o,l=lz_decomp(rom,MAP0,True); w=list(struct.unpack('<2048H',o))
    for r in (0,2,4,6,8,10,12,14,16,18,20,22): put(w,0,r,16,'')
    for r in range(17,32): put(w,1,r,0,'')
    for row,t in TOP:
        put(w,0,row,16,t)
        if row<=14: put(w,1,row+17,0,t)
    c=lz_comp(struct.pack('<2048H',*w))
    assert len(c)<=MAPEND-MAP0, len(c)
    rom[MAP0:MAP0+len(c)]=c
    return len(c)
