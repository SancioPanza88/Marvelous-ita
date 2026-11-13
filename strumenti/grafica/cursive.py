import numpy as np
from PIL import Image, ImageDraw, ImageFont
FONT='/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrechorus-mediumitalic.otf'
def render(text, size=18, bold=1, base=11, maxw=None, sp=1.0):
    f4=ImageFont.truetype(FONT,size*4)
    W=int(f4.getlength(text)/4+len(text)*sp)+12
    im=Image.new('L',(W*4,16*4),0); dr=ImageDraw.Draw(im)
    asc=f4.getmetrics()[0]; x=8.0
    for ch in text:
        dr.text((x,base*4-asc),ch,font=f4,fill=255); x+=f4.getlength(ch)+sp*4
    a=np.array(im.resize((W,16),Image.BOX))
    m=a>70
    if bold:
        m2=m.copy(); m2[:,1:]|=m[:,:-1]; m=m2
    cols=np.where(m.any(axis=0))[0]
    out=np.zeros((16,W+2),np.uint8)
    out[:, :W][m]=3
    # shadow right/below
    sh=np.zeros_like(m); sh[1:,1:]=m[:-1,:-1]
    sh2=np.zeros((16,W+2),bool); sh2[:, :W]=sh
    out[(sh2)&(out==0)]=1
    # left edge highlight color 2
    le=np.zeros((16,W+2),bool); le[:, :W-1]=m[:,1:]&~m[:,:-1]
    out[le&(out==0)]=2
    cols=np.where(out.any(axis=0))[0]
    return out[:, cols.min():cols.max()+1] if len(cols) else out[:, :1]
