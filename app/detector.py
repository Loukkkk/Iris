"""
Detects fullscreen/game/video — no subprocess, no concurrent.futures, no threading.
Uses only ctypes (already loaded by Python) + lazy winrt via QThread.
"""
import ctypes
import ctypes.wintypes

MEDIA_PROCESSES = {
    "vlc.exe", "mpv.exe", "mpc-hc.exe", "mpc-hc64.exe", "mpc-be.exe", "mpc-be64.exe",
    "potplayer.exe", "potplayermini.exe", "potplayermini64.exe", "wmplayer.exe",
    "movies.ui.exe", "hevc.exe", "groove.exe",
}

def _get_foreground_exe() -> str:
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        pid = ctypes.wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid.value)
        if h:
            buf = ctypes.create_unicode_buffer(512)
            sz = ctypes.wintypes.DWORD(512)
            ctypes.windll.kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(sz))
            ctypes.windll.kernel32.CloseHandle(h)
            return buf.value.lower().split("\\")[-1]
    except Exception:
        pass
    return ""

def _is_fullscreen() -> bool:
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd: return False
        hmon = ctypes.windll.user32.MonitorFromWindow(hwnd, 2)
        class MI(ctypes.Structure):
            _fields_ = [("cbSize",ctypes.wintypes.DWORD),("rcMonitor",ctypes.wintypes.RECT),
                        ("rcWork",ctypes.wintypes.RECT),("dwFlags",ctypes.wintypes.DWORD)]
        mi = MI(); mi.cbSize = ctypes.sizeof(MI)
        ctypes.windll.user32.GetMonitorInfoW(hmon, ctypes.byref(mi))
        wr = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(wr))
        m = mi.rcMonitor
        return wr.left<=m.left and wr.top<=m.top and wr.right>=m.right and wr.bottom>=m.bottom
    except Exception:
        return False

def _is_presentation_mode() -> bool:
    try:
        state = ctypes.c_int(0)
        ctypes.windll.shell32.SHQueryUserNotificationState(ctypes.byref(state))
        return state.value in (2, 3, 4)
    except Exception:
        return False

def _is_media_playing() -> bool:
    """
    Check Windows Media Session API using a QThread so we don't
    pull in subprocess/concurrent.futures/threading.
    Only runs if winrt is available (Windows 10+).
    """
    try:
        # Use Qt's event loop integration instead of asyncio
        from PyQt6.QtCore import QThread, pyqtSignal, QObject

        class _Worker(QObject):
            result = pyqtSignal(bool)
            def run(self):
                try:
                    import winrt.windows.media.control as wmc
                    import asyncio
                    async def _check():
                        try:
                            mgr = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
                            for s in mgr.get_sessions():
                                if s.get_playback_info().playback_status.value == 4:
                                    return True
                        except Exception:
                            pass
                        return False
                    loop = asyncio.new_event_loop()
                    try:
                        r = loop.run_until_complete(_check())
                    finally:
                        loop.close()
                    self.result.emit(r)
                except Exception:
                    self.result.emit(False)

        # Run synchronously with a short timeout using Qt event loop
        from PyQt6.QtCore import QEventLoop, QTimer
        _result = [False]
        loop = QEventLoop()
        worker = _Worker()
        thread = QThread()
        worker.moveToThread(thread)
        worker.result.connect(lambda r: (_result.__setitem__(0, r), loop.quit()))
        thread.started.connect(worker.run)
        QTimer.singleShot(800, loop.quit)  # 800ms timeout
        thread.start()
        loop.exec()
        
        if thread.isRunning():
            thread.quit()
            if not thread.wait(200):
                # Thread is still running. Prevent GC crash by keeping a reference.
                global _abandoned_threads
                if '_abandoned_threads' not in globals():
                    _abandoned_threads = []
                _abandoned_threads.append((thread, worker))
                # Clean up old ones
                _abandoned_threads = [(t, w) for t, w in _abandoned_threads if t.isRunning()]
                return False
                
        return _result[0]

    except ImportError:
        return False
    except Exception:
        return False


def should_suppress_alert() -> bool:
    exe = _get_foreground_exe()
    if exe and exe in MEDIA_PROCESSES:
        return True
    if _is_presentation_mode():
        return True
    if _is_fullscreen():
        return True
    if _is_media_playing():
        return True
    return False
