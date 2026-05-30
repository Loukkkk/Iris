"""
EyeRest — Main window.
All layout via standard Qt VBoxLayout with fixed-height wrapper widgets.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QRectF, QRect, pyqtSignal, QSize
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QFont, QIcon, QPixmap,
    QPainterPath, QImage
)
from PIL import Image, ImageDraw
import struct, io

from app.break_overlay import BreakOverlay
from app.startup import set_startup, get_startup


# ── Icon ─────────────────────────────────────────────────────────────────────

def _make_icon_image(s):
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

def _make_ico_bytes():
    sizes = [16,32,48,64,128,256]
    pngs = []
    for s in sizes:
        buf = io.BytesIO(); _make_icon_image(s).save(buf,'PNG',optimize=True); pngs.append(buf.getvalue())
    n = len(sizes); header = struct.pack('<HHH',0,1,n)
    dirs = b''; offset = 6+n*16
    for i,s in enumerate(sizes):
        w = 0 if s==256 else s
        dirs += struct.pack('<BBBBHHII',w,w,0,0,1,32,len(pngs[i]),offset); offset+=len(pngs[i])
    return header+dirs+b''.join(pngs)

def _app_icon():
    icon = QIcon()
    for s in [16,24,32,48,64,128,256]:
        img = _make_icon_image(s)
        buf = io.BytesIO(); img.save(buf,'PNG'); buf.seek(0)
        icon.addPixmap(QPixmap.fromImage(QImage.fromData(buf.read(),'PNG')))
    return icon


# ── Helpers ───────────────────────────────────────────────────────────────────

def lbl(text, size=12, bold=False, color="#C8DCE8"):
    w = QLabel(text)
    w.setFont(QFont("Segoe UI", size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
    w.setStyleSheet(f"color:{color}; background:transparent; border:none;")
    return w

def hline():
    """Fixed-height wrapper for a horizontal row."""
    w = QWidget()
    w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    return w


# ── Custom SpinBox ────────────────────────────────────────────────────────────

class CustomSpinBox(QWidget):
    valueChanged = pyqtSignal(int)
    def __init__(self, minimum=1, maximum=999, value=20, suffix="", parent=None):
        super().__init__(parent)
        self._min=minimum; self._max=maximum; self._val=value; self._suffix=suffix
        self._hover_up=False; self._hover_dn=False
        self.setFixedSize(104,30)
        self.setMouseTracking(True)
    def value(self): return self._val
    def setValue(self, v):
        v=max(self._min,min(self._max,v))
        if v!=self._val: self._val=v; self.valueChanged.emit(v); self.update()
    def _btn_rects(self):
        bw=24; h=self.height(); x=self.width()-bw
        return QRect(x,1,bw-1,h//2-1), QRect(x,h//2,bw-1,h-h//2-1)
    def paintEvent(self,e):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w,h=self.width(),self.height(); bw=24
        path=QPainterPath(); path.addRoundedRect(QRectF(0,0,w,h),7,7)
        p.fillPath(path,QColor("#111C2A"))
        p.setPen(QPen(QColor("#1E3448"),1)); p.drawRoundedRect(QRectF(.5,.5,w-1,h-1),7,7)
        p.setPen(QPen(QColor("#1E3448"),1)); p.drawLine(w-bw,1,w-bw,h-2)
        p.setPen(QColor("#C8DCE8")); p.setFont(QFont("Segoe UI",11))
        p.drawText(QRect(0,0,w-bw,h),Qt.AlignmentFlag.AlignCenter,f"{self._val}{self._suffix}")
        up,dn=self._btn_rects()
        if self._hover_up: p.fillRect(up,QColor("#1A3050"))
        if self._hover_dn: p.fillRect(dn,QColor("#1A3050"))
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor("#5DD4F0"))
        for rect,up_dir in [(up,True),(dn,False)]:
            cx,cy=rect.center().x(),rect.center().y()
            tri=QPainterPath()
            if up_dir: tri.moveTo(cx,cy-3); tri.lineTo(cx-4,cy+2); tri.lineTo(cx+4,cy+2)
            else: tri.moveTo(cx,cy+3); tri.lineTo(cx-4,cy-2); tri.lineTo(cx+4,cy-2)
            tri.closeSubpath(); p.drawPath(tri)
    def mouseMoveEvent(self,e):
        up,dn=self._btn_rects()
        self._hover_up=up.contains(e.pos()); self._hover_dn=dn.contains(e.pos()); self.update()
    def leaveEvent(self,e): self._hover_up=False; self._hover_dn=False; self.update()
    def mousePressEvent(self,e):
        if e.button()==Qt.MouseButton.LeftButton:
            up,dn=self._btn_rects()
            if up.contains(e.pos()): self.setValue(self._val+1)
            elif dn.contains(e.pos()): self.setValue(self._val-1)
    def wheelEvent(self,e): self.setValue(self._val+(1 if e.angleDelta().y()>0 else -1))


# ── Custom CheckBox ───────────────────────────────────────────────────────────

class CustomCheckBox(QWidget):
    toggled = pyqtSignal(bool)
    def __init__(self, text="", checked=False, parent=None):
        super().__init__(parent)
        self._text=text; self._checked=checked; self._hover=False
        self.setMouseTracking(True); self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(26)
    def isChecked(self): return self._checked
    def setChecked(self,v): self._checked=v; self.update()
    def paintEvent(self,e):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        h=self.height(); box=17; by=(h-box)//2
        if self._checked: p.setBrush(QColor("#5DD4F0")); p.setPen(Qt.PenStyle.NoPen)
        else:
            p.setBrush(QColor("#121E2E" if self._hover else "#0F1A28"))
            p.setPen(QPen(QColor("#3A6070" if self._hover else "#1E3448"),1.5))
        p.drawRoundedRect(QRectF(0,by,box,box),4,4)
        if self._checked:
            p.setPen(QPen(QColor("#080E18"),2,Qt.PenStyle.SolidLine,
                         Qt.PenCapStyle.RoundCap,Qt.PenJoinStyle.RoundJoin))
            cx,cy=box//2,by+box//2
            p.drawLine(cx-4,cy,cx-1,cy+3); p.drawLine(cx-1,cy+3,cx+4,cy-3)
        p.setPen(QColor("#C8DCE8" if self._checked else "#8AAFC4"))
        p.setFont(QFont("Segoe UI",11))
        p.drawText(QRect(box+9,0,self.width()-box-9,h),Qt.AlignmentFlag.AlignVCenter,self._text)
    def mousePressEvent(self,e):
        if e.button()==Qt.MouseButton.LeftButton:
            self._checked=not self._checked; self.toggled.emit(self._checked); self.update()
    def enterEvent(self,e): self._hover=True; self.update()
    def leaveEvent(self,e): self._hover=False; self.update()


# ── Ring ─────────────────────────────────────────────────────────────────────

class RingProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 160)
        self._progress=0.0; self._color=QColor("#5DD4F0")
        self._label="00:00"
    def set_progress(self,value,label=""):
        self._progress=max(0.0,min(1.0,value))
        if label: self._label=label
        self.update()
    def set_color(self,c): self._color=c; self.update()
    def paintEvent(self,e):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w,h=self.width(),self.height(); m=12
        rect=QRectF(m,m,w-2*m,h-2*m)
        p.setPen(QPen(QColor(255,255,255,16),10,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap))
        p.drawArc(rect,0,360*16)
        p.setPen(QPen(self._color,10,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap))
        p.drawArc(rect,90*16,-int(self._progress*360*16))
        p.setPen(QColor("#E8F4F8"))
        p.setFont(QFont("Segoe UI",20,QFont.Weight.Bold))
        p.drawText(QRectF(0,0,w,h),Qt.AlignmentFlag.AlignCenter,self._label)


# ── Rounded card background painter ──────────────────────────────────────────

class CardWidget(QWidget):
    """Simple widget that paints a dark rounded card background."""
    def paintEvent(self,e):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path=QPainterPath()
        path.addRoundedRect(QRectF(self.rect()).adjusted(.5,.5,-.5,-.5),12,12)
        p.fillPath(path,QColor("#0D1926"))
        p.setPen(QPen(QColor("#182A3C"),1)); p.drawPath(path)


# ── Stylesheet ────────────────────────────────────────────────────────────────


# ── Info Popup ────────────────────────────────────────────────────────────────

class InfoPopup(QWidget):
    """
    Custom floating popup — no native Windows chrome at all.
    Shows a message with an icon, title, body and a close button.
    """
    def __init__(self, title, body, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.WindowStaysOnTopHint |
                         Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self._title = title
        self._body = body
        self._build()
        self.setFixedWidth(360)

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 10)  # shadow room at bottom
        outer.setSpacing(0)

        card = QWidget()
        card.setObjectName("popcard")
        card.setStyleSheet("""
            QWidget#popcard {
                background-color: #0D1926;
                border: 1px solid #2A4860;
                border-radius: 14px;
            }
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 18, 20, 18)
        cl.setSpacing(10)

        # Icon + title row
        hdr = QHBoxLayout(); hdr.setSpacing(10)
        icon = QLabel("💡")
        icon.setFont(QFont("Segoe UI", 18))
        icon.setStyleSheet("background:transparent; border:none;")
        title_lbl = QLabel(self._title)
        title_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color:#E8F4F8; background:transparent; border:none;")
        title_lbl.setWordWrap(True)
        hdr.addWidget(icon, alignment=Qt.AlignmentFlag.AlignTop)
        hdr.addWidget(title_lbl, 1)
        cl.addLayout(hdr)

        # Separator
        sep = QWidget(); sep.setFixedHeight(1)
        sep.setStyleSheet("background:#182A3C; border:none;")
        cl.addWidget(sep)

        # Body
        body_lbl = QLabel(self._body)
        body_lbl.setFont(QFont("Segoe UI", 11))
        body_lbl.setStyleSheet("color:#8AAFC4; background:transparent; border:none;")
        body_lbl.setWordWrap(True)
        cl.addWidget(body_lbl)

        # Close button
        btn = QPushButton("OK, compris")
        btn.setObjectName("primary")
        btn.setFixedHeight(34)
        btn.clicked.connect(self.hide)
        cl.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)

        outer.addWidget(card)

    def show_near(self, parent_widget):
        """Show the popup centered above the parent window."""
        self.adjustSize()
        if parent_widget:
            pg = parent_widget.frameGeometry()
            x = pg.center().x() - self.width() // 2
            y = pg.center().y() - self.height() // 2
            self.move(x, y)
        self.show()
        self.raise_()


STYLE = """
QMainWindow { background-color: #080E18; }
QWidget { background-color: transparent; font-family: 'Segoe UI'; }
QWidget#root { background-color: #080E18; }
QLabel { background: transparent; border: none; }
QPushButton { outline:none; border:none; font-family:'Segoe UI'; }
QPushButton#primary {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #5DD4F0,stop:1 #2FA8D4);
    color:#050D18; border-radius:10px; font-size:13px; font-weight:700; padding:9px 24px;
}
QPushButton#primary:hover { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #7AE0F8,stop:1 #3DC0EC); }
QPushButton#secondary {
    background-color:#111C2A; color:#8AAFC4; border:1px solid #1E3448;
    border-radius:10px; font-size:12px; padding:7px 18px;
}
QPushButton#secondary:hover { background-color:#162030; color:#C8DCE8; border-color:#2A4860; }
"""


# ── Main Window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self._settings=settings; self._overlay=BreakOverlay(); self._engine=None
        self._icon=_app_icon()
        self.setWindowTitle("EyeRest"); self.setWindowIcon(self._icon)
        self.setFixedWidth(480)
        self.setStyleSheet(STYLE)
        self._ready = False  # blocks showEvent until we are ready
        self._build_ui()

    def get_icon(self): return self._icon

    def showEvent(self, event):
        if not self._ready:
            self._ready = True
            # Compute correct height before first paint
            hint = self.centralWidget().sizeHint()
            if hint.isValid() and hint.height() > 100:
                self.resize(self.width(), hint.height() + 32)
        super().showEvent(event)

    def set_engine(self, engine):
        self._engine=engine; engine.tick.connect(self._on_tick)

    def _build_ui(self):
        root=QWidget(); root.setObjectName("root")
        self.setCentralWidget(root)
        main=QVBoxLayout(root)
        main.setContentsMargins(20,18,20,14)
        main.setSpacing(10)

        # ── Header ──
        hdr=QHBoxLayout(); hdr.setSpacing(10)
        icon_lbl=QLabel()
        img=_make_icon_image(40); buf=io.BytesIO(); img.save(buf,'PNG'); buf.seek(0)
        icon_lbl.setPixmap(QPixmap.fromImage(QImage.fromData(buf.read(),'PNG')).scaled(
            32,32,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        icon_lbl.setFixedSize(36,36)
        hv=QVBoxLayout(); hv.setSpacing(0)
        hv.addWidget(lbl("EyeRest",16,bold=True,color="#E8F4F8"))
        hv.addWidget(lbl("Protection des yeux",9,color="#5DD4F0"))
        hdr.addWidget(icon_lbl); hdr.addLayout(hv); hdr.addStretch()
        main.addLayout(hdr)

        # ── Ring card ──
        rc=CardWidget()
        rl=QVBoxLayout(rc); rl.setContentsMargins(16,14,16,12); rl.setSpacing(6)
        rl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._ring=RingProgress()
        rl.addWidget(self._ring, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._status_lbl=lbl("🟢  En cours de travail",10,color="#4A8A9A")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rl.addWidget(self._status_lbl)
        main.addWidget(rc)

        # ── Config card ──
        cc=CardWidget()
        cl=QVBoxLayout(cc); cl.setContentsMargins(18,14,18,12); cl.setSpacing(0)

        cl.addWidget(lbl("Configuration",11,bold=True,color="#E8F4F8"))
        cl.addSpacing(10)

        # Row helper — fixed height 32px per row
        def spin_row(label_text, spin):
            row=QWidget(); row.setFixedHeight(32)
            hl=QHBoxLayout(row); hl.setContentsMargins(0,0,0,0); hl.setSpacing(0)
            hl.addWidget(lbl(label_text,11),alignment=Qt.AlignmentFlag.AlignVCenter)
            hl.addStretch()
            hl.addWidget(spin,alignment=Qt.AlignmentFlag.AlignVCenter)
            return row

        self._work_spin=CustomSpinBox(1,120,self._settings.get("work_interval_min",20)," min")
        self._work_spin.valueChanged.connect(lambda v:self._settings.set("work_interval_min",v))
        cl.addWidget(spin_row("Travail entre les pauses",self._work_spin))
        cl.addSpacing(6)

        self._break_spin=CustomSpinBox(5,300,self._settings.get("break_duration_sec",20)," sec")
        self._break_spin.valueChanged.connect(lambda v:self._settings.set("break_duration_sec",v))
        cl.addWidget(spin_row("Durée de la pause",self._break_spin))
        cl.addSpacing(8)

        cl.addWidget(lbl("📏  Regardez à 20 pieds (6 m) — règle 20-20-20",9,color="#2E5060"))
        main.addWidget(cc)

        # ── Options card ──
        oc=CardWidget()
        ol=QVBoxLayout(oc); ol.setContentsMargins(18,12,18,12); ol.setSpacing(6)

        ol.addWidget(lbl("Options",11,bold=True,color="#E8F4F8"))
        ol.addSpacing(4)

        self._chk_fs=CustomCheckBox("Ne pas alerter en plein écran / jeu / vidéo",
                                    checked=self._settings.get("skip_fullscreen",True))
        self._chk_fs.toggled.connect(lambda v:self._settings.set("skip_fullscreen",v))
        ol.addWidget(self._chk_fs)

        self._chk_bg=CustomCheckBox("Réduire en arrière-plan à la fermeture",
                                    checked=self._settings.get("background_mode",True))
        self._chk_bg.toggled.connect(self._on_bg_toggled)
        ol.addWidget(self._chk_bg)

        self._chk_startup=CustomCheckBox("Démarrer avec Windows",checked=get_startup())
        self._chk_startup.toggled.connect(self._on_startup_toggled)
        ol.addWidget(self._chk_startup)

        self._chk_min=CustomCheckBox("   ↳  Démarrer directement en arrière-plan",
                                     checked=self._settings.get("start_minimized",False))
        self._chk_min.toggled.connect(lambda v:self._settings.set("start_minimized",v))
        self._chk_min.setVisible(self._settings.get("background_mode",True) and get_startup())
        ol.addWidget(self._chk_min)
        main.addWidget(oc)

        # ── Buttons ──
        main.addSpacing(2)
        br=QHBoxLayout(); br.setSpacing(10)
        self._pause_btn=QPushButton("⏸  Pause"); self._pause_btn.setObjectName("secondary")
        self._pause_btn.clicked.connect(self._toggle_pause)
        self._break_btn=QPushButton("Pause maintenant"); self._break_btn.setObjectName("primary")
        self._break_btn.clicked.connect(self._break_now)
        br.addWidget(self._pause_btn); br.addStretch(); br.addWidget(self._break_btn)
        main.addLayout(br)

        footer=lbl("Règle 20-20-20 — toutes les 20 min, 20 sec à 20 pieds (6 m)",8,color="#1A3040")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(footer)

    def _on_bg_toggled(self,v):
        self._settings.set("background_mode",v)
        self._chk_min.setVisible(v and self._chk_startup.isChecked())

    def _on_startup_toggled(self,v):
        self._settings.set("start_with_windows",v)
        set_startup(v)
        self._chk_min.setVisible(v and self._chk_bg.isChecked())
        if v:
            if not hasattr(self, '_startup_popup'):
                self._startup_popup = InfoPopup(
                    "Démarrage avec Windows activé",
                    "Si vous déplacez l'exécutable vers un autre dossier, "
                    "relancez-le une fois pour que le démarrage automatique "
                    "pointe vers le bon emplacement.",
                    self
                )
            self._startup_popup.show_near(self)

    def _on_tick(self,elapsed,total,state):
        from app.timer_engine import TimerEngine
        if state==TimerEngine.STATE_WORKING:
            m,s=divmod(total-elapsed,60)
            self._ring.set_progress(elapsed/max(total,1),f"{m:02d}:{s:02d}")
            self._ring.set_color(QColor("#5DD4F0"))
            self._status_lbl.setText("🟢  En cours de travail")
        elif state==TimerEngine.STATE_BREAK:
            self._ring.set_progress(1.0-elapsed/max(total,1),str(total-elapsed))
            self._ring.set_color(QColor("#50F0A0"))
            self._status_lbl.setText("🌿  Pause — regardez au loin")
        elif state==TimerEngine.STATE_SUPPRESSED:
            self._ring.set_progress(1.0,"⏳")
            self._ring.set_color(QColor("#F0B050"))
            self._status_lbl.setText("🎮  Fullscreen détecté — pause en attente")
        elif state==TimerEngine.STATE_PAUSED:
            self._ring.set_color(QColor("#3A5060"))
            self._status_lbl.setText("⏸  En pause")

    def _toggle_pause(self):
        if not self._engine: return
        from app.timer_engine import TimerEngine
        if self._engine.state==TimerEngine.STATE_PAUSED:
            self._engine.resume(); self._pause_btn.setText("⏸  Pause")
        else:
            self._engine.pause(); self._pause_btn.setText("▶  Reprendre")

    def _break_now(self):
        if self._engine:
            self._engine.reset(); self._engine._elapsed=self._engine._work_total()

    def show_break_overlay(self,duration):
        self._overlay.show_overlay(duration,on_skip=self._engine.skip_break if self._engine else None)

    def update_break_countdown(self,remaining):
        self._overlay.update_countdown(remaining)

    def hide_break_overlay(self):
        self._overlay.hide_overlay()

    def closeEvent(self,event):
        if self._settings.get("background_mode",True): event.ignore(); self.hide()
        else: event.accept()
