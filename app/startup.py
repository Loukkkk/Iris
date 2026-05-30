"""
Windows startup registry — adds/removes EyeRest from HKCU Run key.
Auto-updates the path every launch if the exe has moved.
"""
import sys
import os

APP_NAME = "Iris"
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _get_exe_path() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}" --startup'
    else:
        main = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
        return f'"{sys.executable}" "{main}" --startup'


def set_startup(enable: bool) -> bool:
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        if enable:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _get_exe_path())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"[startup] Error: {e}")
        return False


def get_startup() -> bool:
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, APP_NAME)
            found = True
        except FileNotFoundError:
            found = False
        winreg.CloseKey(key)
        return found
    except Exception:
        return False


def get_registered_path() -> str:
    """Returns the currently registered exe path in the registry."""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        try:
            val, _ = winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return val
        except FileNotFoundError:
            winreg.CloseKey(key)
    except Exception:
        pass
    return ""


def auto_update_startup_path():
    """
    Called at every launch. If startup is enabled but the registered path
    doesn't match the current exe location, silently update the registry.
    """
    if not get_startup():
        return  # startup not enabled, nothing to do

    current = _get_exe_path()
    registered = get_registered_path()

    if current != registered:
        set_startup(True)
        print(f"[startup] Path updated: {current}")
