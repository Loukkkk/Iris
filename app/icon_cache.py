"""
Icon cache — generates the icon once, saves to AppData, reuses on next launch.
This eliminates the ~500ms Pillow generation delay at startup.
"""
import os
import struct
import io
from pathlib import Path


CACHE_PATH = Path(os.getenv("APPDATA", ".")) / "Iris" / "icon_cache.ico"


def _make_icon_image(s):
    from PIL import Image, ImageDraw
    S = s * 2
    img = Image.new('RGBA', (S, S), (0,0,0,0))
    d = ImageDraw.Draw(img)
    r = max(2, int(S*0.22))
    d.rounded_rectangle([0,0,S-1,S-1], radius=r, fill=(10,18,32,255))
    ew,eh = int(S*0.72),int(S*0.41); ex,ey=(S-ew)//2,(S-eh)//2
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


def _build_ico_bytes():
    sizes = [16,32,48,64,128,256]
    pngs = []
    for s in sizes:
        buf = io.BytesIO()
        _make_icon_image(s).save(buf,'PNG',optimize=True)
        pngs.append(buf.getvalue())
    n = len(sizes)
    header = struct.pack('<HHH',0,1,n)
    dirs = b''; offset = 6+n*16
    for i,s in enumerate(sizes):
        w = 0 if s==256 else s
        dirs += struct.pack('<BBBBHHII',w,w,0,0,1,32,len(pngs[i]),offset)
        offset += len(pngs[i])
    return header + dirs + b''.join(pngs)


def get_ico_bytes() -> bytes:
    """Return ICO bytes from cache, generating if needed."""
    if CACHE_PATH.exists():
        try:
            return CACHE_PATH.read_bytes()
        except Exception:
            pass
    # Generate and cache
    data = _build_ico_bytes()
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_bytes(data)
    except Exception:
        pass
    return data


def get_ico_path() -> str:
    """Return path to cached .ico file, generating if needed."""
    if not CACHE_PATH.exists():
        get_ico_bytes()
    return str(CACHE_PATH)


def build_qicon():
    """Build QIcon from cached ICO bytes — fast on second launch."""
    from PyQt6.QtGui import QIcon, QPixmap, QImage
    data = get_ico_bytes()
    icon = QIcon()
    # Load each size individually for best quality
    sizes = [16,24,32,48,64,128,256]
    if CACHE_PATH.exists():
        # Fast path: load from cached file per size
        for s in sizes:
            px = QPixmap(str(CACHE_PATH))
            if not px.isNull():
                icon.addPixmap(px.scaled(s, s))
    else:
        # Fallback: load from bytes
        px = QPixmap()
        px.loadFromData(data, 'ICO')
        icon.addPixmap(px)
    return icon


def invalidate_cache():
    """Delete cached icon (call if icon design changes)."""
    try:
        CACHE_PATH.unlink()
    except Exception:
        pass
