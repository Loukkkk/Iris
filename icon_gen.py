from PIL import Image, ImageDraw
import struct, io

def make_img(s):
    S = s * 2
    img = Image.new('RGBA', (S, S), (0,0,0,0))
    d = ImageDraw.Draw(img)
    r = max(2, int(S*0.22))
    d.rounded_rectangle([0,0,S-1,S-1], radius=r, fill=(10,18,32,255))
    ew,eh = int(S*0.72),int(S*0.41)
    ex,ey = (S-ew)//2,(S-eh)//2
    d.ellipse([ex,ey,ex+ew,ey+eh], fill=(215,238,248,255))
    ir=int(S*0.185); cx,cy=S//2,S//2
    d.ellipse([cx-ir,cy-ir,cx+ir,cy+ir], fill=(35,175,220,255))
    ir2=int(S*0.13)
    d.ellipse([cx-ir2,cy-ir2,cx+ir2,cy+ir2], fill=(75,210,245,255))
    pr=int(S*0.08)
    d.ellipse([cx-pr,cy-pr,cx+pr,cy+pr], fill=(5,10,22,255))
    hr=max(2,int(S*0.052)); hx=cx+int(ir*0.20); hy=cy-int(ir*0.46)
    d.ellipse([hx,hy,hx+hr*2,hy+hr*2], fill=(255,255,255,220))
    return img.resize((s,s), Image.LANCZOS)

sizes = [16,32,48,64,128,256]
pngs = []
for s in sizes:
    buf = io.BytesIO()
    make_img(s).save(buf,'PNG',optimize=True)
    pngs.append(buf.getvalue())

n = len(sizes)
header = struct.pack('<HHH', 0, 1, n)
dirs = b''
offset = 6 + n*16
for i,s in enumerate(sizes):
    w = 0 if s==256 else s
    dirs += struct.pack('<BBBBHHII', w, w, 0, 0, 1, 32, len(pngs[i]), offset)
    offset += len(pngs[i])

with open('icon.ico','wb') as f:
    f.write(header + dirs + b''.join(pngs))

print(f'  icon.ico genere ({len(header+dirs)+sum(len(p) for p in pngs)} bytes)')
