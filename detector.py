"""
Detects if the user is watching a video, playing a game, or using a fullscreen app.
Uses Windows API via ctypes + Windows Media Session API via winrt.
"""
import ctypes
import ctypes.wintypes


# ── Known media process names ─────────────────────────────────────────────────

MEDIA_PROCESSES = {
    "vlc.exe", "mpv.exe", "mpc-hc.exe", "mpc-hc64.exe", "mpc-be.exe", "mpc-be64.exe",
    "potplayer.exe", "potplayermini.exe", "potplayermini64.exe", "wmplayer.exe",
    "movies.ui.exe", "hevc.exe", "groove.exe",
}


# ── Method 1: foreground process name ────────────────────────────────────────

def _get_foreground_exe() -> str:
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        pid = ctypes.wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
        if handle:
            buf = ctypes.create_unicode_buffer(512)
            size = ctypes.wintypes.DWORD(512)
            ctypes.windll.kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size))
            ctypes.windll.kernel32.CloseHandle(handle)
            return buf.value.lower().split("\\")[-1]
    except Exception:
        pass
    return ""


# ── Method 2: fullscreen detection ───────────────────────────────────────────

def _is_fullscreen() -> bool:
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return False
        MONITOR_DEFAULTTONEAREST = 2
        hmon = ctypes.windll.user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)

        class MONITORINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.wintypes.DWORD),
                ("rcMonitor", ctypes.wintypes.RECT),
                ("rcWork", ctypes.wintypes.RECT),
                ("dwFlags", ctypes.wintypes.DWORD),
            ]

        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(MONITORINFO)
        ctypes.windll.user32.GetMonitorInfoW(hmon, ctypes.byref(mi))
        wr = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(wr))
        mon = mi.rcMonitor
        return (wr.left <= mon.left and wr.top <= mon.top
                and wr.right >= mon.right and wr.bottom >= mon.bottom)
    except Exception:
        return False


# ── Method 3: Windows notification state (D3D games, presentation mode) ──────

def _is_presentation_mode() -> bool:
    try:
        QUNS_RUNNING_D3D_FULL_SCREEN = 3
        QUNS_PRESENTATION_MODE = 4
        QUNS_BUSY = 2
        state = ctypes.c_int(0)
        ctypes.windll.shell32.SHQueryUserNotificationState(ctypes.byref(state))
        return state.value in (QUNS_RUNNING_D3D_FULL_SCREEN, QUNS_PRESENTATION_MODE, QUNS_BUSY)
    except Exception:
        return False


# ── Method 4: Windows Media Session API (winrt) ───────────────────────────────
# Detects any media playback (even windowed) via the system media transport controls.
# This catches: Spotify, Netflix in browser, any app using MediaPlayer API,
# streaming apps in windowed mode, etc.

def _is_media_playing() -> bool:
    """
    Returns True if any app is currently playing media via the
    Windows GlobalSystemMediaTransportControls (SMTC) API.
    Works for windowed video/audio players, browsers with media, etc.
    """
    try:
        # Try winrt first (Windows 10+)
        import winrt.windows.media.control as wmc
        import asyncio

        async def _check():
            try:
                manager = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
                sessions = manager.get_sessions()
                for session in sessions:
                    info = await session.try_get_media_properties_async()
                    status = session.get_playback_info()
                    # PlaybackStatus: 4 = Playing
                    if status.playback_status.value == 4:
                        return True
                return False
            except Exception:
                return False

        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            return loop.run_until_complete(_check())
        except RuntimeError:
            # Already running loop (shouldn't happen in our timer thread)
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                future = ex.submit(asyncio.run, _check())
                return future.result(timeout=1.0)

    except ImportError:
        # winrt not installed — fall back silently
        return False
    except Exception:
        return False


# ── Public API ────────────────────────────────────────────────────────────────

def should_suppress_alert() -> bool:
    """
    Returns True if the user appears to be watching a video, playing a game,
    or otherwise in an immersive session.

    Detection methods (in order of cost):
      1. Known media player process name (free)
      2. Windows notification state / D3D fullscreen (free)
      3. Generic fullscreen window (free)
      4. Windows Media Session API — catches windowed streaming (async, ~1ms)
    """
    exe = _get_foreground_exe()

    # Known media player?
    if exe and exe in MEDIA_PROCESSES:
        return True

    # D3D fullscreen / presentation mode?
    if _is_presentation_mode():
        return True

    # Generic fullscreen?
    if _is_fullscreen():
        return True

    # Media playing via SMTC (windowed Netflix, Spotify, etc.)
    if _is_media_playing():
        return True

    return False
