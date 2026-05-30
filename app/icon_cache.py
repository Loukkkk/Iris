"""
Icon cache — loads the bundled icon.ico directly.
No Pillow, no subprocess, no threading overhead.
The icon.ico is generated once by icon_gen.py and shipped with the app.
"""
import os
import gc
import sys
from pathlib import Path


def _bundled_ico() -> str:
    """Path to the bundled icon.ico (next to main.py or in PyInstaller bundle)."""
    # PyInstaller bundle: files are extracted in sys._MEIPASS at runtime
    if hasattr(sys, '_MEIPASS'):
        base = Path(sys._MEIPASS)
    else:
        # Script mode: go up one directory from app/ to reach the root iris/ folder
        base = Path(__file__).resolve().parent.parent
        
    return str(base / 'icon.ico')


def get_ico_path() -> str:
    return _bundled_ico()


def build_qicon():
    """Build QIcon from bundled icon.ico — fast, no PIL, no subprocess."""
    from PyQt6.QtGui import QIcon, QPixmap
    from PyQt6.QtCore import Qt

    ico_path = _bundled_ico()
    icon = QIcon()
    px = QPixmap(ico_path)
    if not px.isNull():
        for s in [16, 24, 32, 48, 64, 128, 256]:
            icon.addPixmap(px.scaled(
                s, s,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
    del px
    gc.collect()
    return icon