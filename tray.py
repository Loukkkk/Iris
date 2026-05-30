"""
System tray icon and menu.
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QAction
from PyQt6.QtCore import Qt, QSize


def _make_tray_icon() -> QIcon:
    """Create a simple eye icon programmatically."""
    px = QPixmap(64, 64)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor("#5DD4F0"))
    p.setPen(Qt.PenStyle.NoPen)
    # Outer eye shape (ellipse)
    p.drawEllipse(4, 18, 56, 28)
    # Pupil white
    p.setBrush(QColor("#080E18"))
    p.drawEllipse(22, 22, 20, 20)
    # Iris
    p.setBrush(QColor("#5DD4F0"))
    p.drawEllipse(26, 26, 12, 12)
    p.end()
    return QIcon(px)


class SystemTray(QSystemTrayIcon):
    def __init__(self, settings, main_window, engine, app):
        super().__init__()
        self._settings = settings
        self._window = main_window
        self._engine = engine
        self._app = app

        self.setIcon(_make_tray_icon())
        self.setToolTip("EyeRest")
        self._build_menu()
        self.activated.connect(self._on_activate)

        # Wire engine ticks to overlay countdown update
        engine.tick.connect(self._on_tick)

    def _build_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background: #0E1A28;
                color: #C8DCE8;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 4px;
                font-family: "Segoe UI";
                font-size: 13px;
            }
            QMenu::item { padding: 6px 18px; border-radius: 5px; }
            QMenu::item:selected { background: rgba(93,212,240,0.15); }
            QMenu::separator { height: 1px; background: rgba(255,255,255,0.07); margin: 4px 10px; }
        """)

        act_show = QAction("Ouvrir EyeRest", self)
        act_show.triggered.connect(self._show_window)
        menu.addAction(act_show)

        menu.addSeparator()

        self._act_pause = QAction("⏸  Mettre en pause", self)
        self._act_pause.triggered.connect(self._toggle_pause)
        menu.addAction(self._act_pause)

        act_break = QAction("🌿  Pause maintenant", self)
        act_break.triggered.connect(self._break_now)
        menu.addAction(act_break)

        menu.addSeparator()

        act_quit = QAction("Quitter", self)
        act_quit.triggered.connect(self._quit)
        menu.addAction(act_quit)

        self.setContextMenu(menu)

    def _on_activate(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_window()

    def _show_window(self):
        self._window.show()
        self._window.raise_()
        self._window.activateWindow()

    def _toggle_pause(self):
        from app.timer_engine import TimerEngine
        if self._engine.state == TimerEngine.STATE_PAUSED:
            self._engine.resume()
            self._act_pause.setText("⏸  Mettre en pause")
        else:
            self._engine.pause()
            self._act_pause.setText("▶  Reprendre")

    def _break_now(self):
        self._engine.reset()
        self._engine._elapsed = self._engine._work_total()

    def _quit(self):
        self._engine.stop()
        self._app.quit()

    def update_tooltip(self, text: str):
        self.setToolTip(text)

    def _on_tick(self, elapsed, total, state):
        from app.timer_engine import TimerEngine
        if state == TimerEngine.STATE_BREAK:
            self._window.update_break_countdown(total - elapsed)
