"""
Iris - Eye protection app (20-20-20 rule)
"""
import sys
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer

from app.tray import SystemTray
from app.startup import auto_update_startup_path
from app.icon_cache import build_qicon, get_ico_path
from app.settings import Settings
from app.timer_engine import TimerEngine


def _launched_at_startup():
    return "--startup" in sys.argv


def _single_instance():
    try:
        ctypes.windll.kernel32.CreateMutexW(None, True, "IrisSingleInstanceMutex")
        return ctypes.windll.kernel32.GetLastError() != 183
    except Exception:
        return True


def _set_taskbar_icon(hwnd):
    try:
        path = get_ico_path()
        LR_LOADFROMFILE = 0x10; IMAGE_ICON = 1
        hl = ctypes.windll.user32.LoadImageW(None, path, IMAGE_ICON, 256, 256, LR_LOADFROMFILE)
        hs = ctypes.windll.user32.LoadImageW(None, path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
        ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, hs)
        ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, hl)
    except Exception:
        pass


def main():
    if not _single_instance():
        sys.exit(0)

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("iris.eyeprotection.app.1")
    except Exception:
        pass

    try:
        import pyi_splash
        pyi_splash.close()
    except Exception:
        pass

    auto_update_startup_path()

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("Iris")

    icon = build_qicon()
    app.setWindowIcon(icon)

    settings = Settings()

    if _launched_at_startup() and settings.get("start_minimized") and settings.get("start_with_windows"):
        from app.main_window import MainWindow
        window = MainWindow(settings)
        window.setWindowIcon(icon)
        engine = TimerEngine(settings)
        window.set_engine(engine)
        tray = SystemTray(settings, window, engine, app)
        tray.setIcon(icon)
        window.set_tray_ref(tray)
        engine.set_tray(tray)
        engine.set_main_window(window)
        engine.start()
        tray.show()
    else:
        engine = TimerEngine(settings)
        engine.start()

        def _create_and_show():
            from app.main_window import MainWindow
            window = MainWindow(settings)
            window.setWindowIcon(icon)
            window.set_engine(engine)

            tray = SystemTray(settings, window, engine, app)
            tray.setIcon(icon)
            window.set_tray_ref(tray)
            engine.set_tray(tray)
            engine.set_main_window(window)
            tray.show()

            screen = app.primaryScreen().availableGeometry()
            window.move(
                screen.center().x() - window.width() // 2,
                screen.center().y() - window.height() // 2
            )
            window.show()

            try:
                _set_taskbar_icon(int(window.winId()))
            except Exception:
                pass

        QTimer.singleShot(0, _create_and_show)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
