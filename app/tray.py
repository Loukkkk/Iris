from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction, QCursor
from PyQt6.QtCore import Qt


def _make_tray_icon() -> QIcon:
    px = QPixmap(64, 64); px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor("#5DD4F0")); p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(4,18,56,28)
    p.setBrush(QColor("#080E18")); p.drawEllipse(22,22,20,20)
    p.setBrush(QColor("#5DD4F0")); p.drawEllipse(26,26,12,12)
    p.end()
    return QIcon(px)


class SystemTray(QSystemTrayIcon):
    def __init__(self, settings, main_window, engine, app):
        super().__init__()
        self._settings=settings; self._window=main_window
        self._engine=engine; self._app=app
        self.setIcon(_make_tray_icon())
        self.setToolTip("Iris")
        self._build_menu()
        self.activated.connect(self._on_activate)
        engine.tick.connect(self._on_tick)

    def t(self, key): return self._window.t(key)

    def _build_menu(self):
        self._menu=QMenu()
        self._menu.setStyleSheet("""
            QMenu{background:#0E1A28;color:#C8DCE8;border:1px solid rgba(255,255,255,0.1);
            border-radius:8px;padding:4px;font-family:"Segoe UI";font-size:13px;}
            QMenu::item{padding:6px 18px;border-radius:5px;}
            QMenu::item:selected{background:rgba(93,212,240,0.15);}
            QMenu::separator{height:1px;background:rgba(255,255,255,0.07);margin:4px 10px;}""")

        act_show=QAction(self.t("tray_open"),self)
        act_show.triggered.connect(self._show_window); self._menu.addAction(act_show)
        self._menu.addSeparator()

        self._act_pause=QAction(self.t("tray_pause"),self)
        self._act_pause.triggered.connect(self._toggle_pause); self._menu.addAction(self._act_pause)

        act_break=QAction(self.t("tray_break"),self)
        act_break.triggered.connect(self._break_now); self._menu.addAction(act_break)
        self._menu.addSeparator()

        act_quit=QAction(self.t("tray_quit"),self)
        act_quit.triggered.connect(self._quit); self._menu.addAction(act_quit)

    def rebuild_menu(self):
        self._build_menu()

    def _on_activate(self,reason):
        if reason==QSystemTrayIcon.ActivationReason.Trigger: 
            self._show_window()
        elif reason==QSystemTrayIcon.ActivationReason.Context:
            # Fix for Windows tray menu focus bug
            self._menu.activateWindow()
            try:
                import ctypes
                hwnd = int(self._menu.winId())
                ctypes.windll.user32.SetForegroundWindow(hwnd)
            except Exception:
                pass
            self._menu.popup(QCursor.pos())

    def _show_window(self):
        self._window.show(); self._window.raise_(); self._window.activateWindow()

    def _toggle_pause(self):
        from app.timer_engine import TimerEngine
        if self._engine.state==TimerEngine.STATE_PAUSED:
            self._engine.resume(); self._act_pause.setText(self.t("tray_pause"))
        else:
            self._engine.pause(); self._act_pause.setText(self.t("tray_resume"))

    def _break_now(self):
        self._engine.reset(); self._engine._elapsed=self._engine._work_total()

    def _quit(self):
        self._engine.stop(); self._app.quit()

    def update_tooltip(self,text): self.setToolTip(text)

    def _on_tick(self,elapsed,total,state):
        from app.timer_engine import TimerEngine
        if state==TimerEngine.STATE_WORKING:
            remaining=total-elapsed; m,s=divmod(remaining,60)
            self.setToolTip(f"{self.t('tray_next')} {m:02d}:{s:02d}")
        elif state==TimerEngine.STATE_SUPPRESSED:
            self.setToolTip(self.t("tray_waiting"))
        elif state==TimerEngine.STATE_BREAK:
            self._window.update_break_countdown(total-elapsed)
