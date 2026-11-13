import sys, numpy as np
sys.path.insert(0,'/home/claude/emu'); from cursive import render
RANGES=[(0,26),(26,50),(50,76),(76,88),(88,114),(114,140),(140,162),(162,184),(184,200)]
LINES=["Tanto tempo fa, i mari erano",
"dominati da avidi pirati.",
"Tra loro, il più famoso era il",
"Cap. Maverick.",
"Si narra che il suo tesoro,",
"il \"Marvelous\", sia protetto da",
"enigmi e creature bizzarre.",
"Chi parte alla sua ricerca",
"non fa più ritorno"]
def build(S_en):
    S=S_en.copy(); S[:, :200*8]=0
    for (a,b),t in zip(RANGES,LINES):
        W=(b-a)*8
        for sz,sp in ((18,1.0),(18,0.5),(17,0.5),(17,0.0),(16,0.0)):
            r=render(t,sz,sp=sp)
            if r.shape[1]<=W-2: break
        else: raise SystemExit('troppo lunga: '+t)
        x=a*8+(W-r.shape[1])//2 if (a,b)!=(184,200) else a*8+W-r.shape[1]-1
        S[:, x:x+r.shape[1]]=r
        print('%-36s %3d/%3d px (size %d sp %.1f)'%(t,r.shape[1],W,sz,sp))
    return S
