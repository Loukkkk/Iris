# PyInstaller runtime hook — runs before main.py
# Hides any window created by the bootloader immediately
import ctypes
import sys

try:
    # Find and hide the console/ghost window the bootloader may have created
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE
except Exception:
    pass

try:
    # Also hide via EnumWindows — find window belonging to this process
    pid = ctypes.windll.kernel32.GetCurrentProcessId()
    
    found = []
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    
    def callback(hwnd, lParam):
        w_pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(w_pid))
        if w_pid.value == pid:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
        return True
    
    ctypes.windll.user32.EnumWindows(EnumWindowsProc(callback), 0)
except Exception:
    pass
