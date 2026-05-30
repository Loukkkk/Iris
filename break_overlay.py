"""
Break overlay — a translucent full-screen reminder to rest eyes.
Designed to be calm, non-intrusive, with a countdown.
"""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QRect
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QFontDatabase


class BreakOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.WindowStaysOnTopHint |
                         Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.setWindowOpacity(0.0)

        self._duration = 20
        self._remaining = 20
        self._alpha = 0
        self._on_skip = None

        self._setup_ui()
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(600)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(24)

        # Eye icon (unicode)
        self._icon_lbl = QLabel("👁", self)
        self._icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_lbl.setStyleSheet("font-size: 64px; background: transparent;")

        # Main message
        self._title_lbl = QLabel("Pause pour vos yeux", self)
        self._title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_lbl.setStyleSheet("""
            color: #E8F4F8;
            font-size: 36px;
            font-weight: 700;
            letter-spacing: 1px;
            background: transparent;
        """)

        # Sub message
        self._sub_lbl = QLabel("Regardez à 6 mètres minimum", self)
        self._sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sub_lbl.setStyleSheet("""
            color: rgba(232, 244, 248, 0.75);
            font-size: 18px;
            background: transparent;
        """)

        # Countdown
        self._count_lbl = QLabel("20", self)
        self._count_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._count_lbl.setStyleSheet("""
            color: #5DD4F0;
            font-size: 72px;
            font-weight: 300;
            background: transparent;
        """)

        # Skip button
        self._skip_btn = QPushButton("Passer", self)
        self._skip_btn.setFixedSize(120, 38)
        self._skip_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.08);
                color: rgba(232, 244, 248, 0.6);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 19px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.15);
                color: #E8F4F8;
            }
        """)
        self._skip_btn.clicked.connect(self._skip)

        layout.addStretch()
        layout.addWidget(self._icon_lbl)
        layout.addWidget(self._title_lbl)
        layout.addWidget(self._sub_lbl)
        layout.addSpacing(12)
        layout.addWidget(self._count_lbl)
        layout.addSpacing(16)
        layout.addWidget(self._skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Deep blue-teal overlay
        painter.fillRect(self.rect(), QColor(8, 20, 35, 210))

    def show_overlay(self, duration: int, on_skip=None):
        from PyQt6.QtWidgets import QApplication
        self._duration = duration
        self._remaining = duration
        self._on_skip = on_skip
        self._count_lbl.setText(str(duration))

        # Cover all screens
        screen = QApplication.primaryScreen()
        geom = screen.geometry()
        self.setGeometry(geom)
        self.showFullScreen()

        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

    def update_countdown(self, remaining: int):
        self._remaining = remaining
        self._count_lbl.setText(str(remaining))

    def hide_overlay(self):
        self._anim.setStartValue(self.windowOpacity())
        self._anim.setEndValue(0.0)
        self._anim.finished.connect(self._after_hide)
        self._anim.start()

    def _after_hide(self):
        try:
            self._anim.finished.disconnect(self._after_hide)
        except Exception:
            pass
        self.hide()

    def _skip(self):
        self.hide_overlay()
        if self._on_skip:
            self._on_skip()
