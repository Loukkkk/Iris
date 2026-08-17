"""
Iris Launcher — single exe entry point.
Extracts the bundled Iris_app/ folder to %LOCALAPPDATA%\Iris\app\ on first
launch (or when updated), then starts Iris_app.exe with SW_HIDE so Windows
never renders a ghost window.
"""
import sys
import os
import subprocess
import hashlib
import shutil
import zipfile
import io


def _get_bundle_data() -> bytes:
    """Read the bundled Iris_app.zip from the PyInstaller bundle."""
    if hasattr(sys, "_MEIPASS"):
        path = os.path.join(sys._MEIPASS, "Iris_app.zip")
    else:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Iris_app.zip")
    with open(path, "rb") as f:
        return f.read()


def _extract_app() -> str:
    """
    Extract Iris_app.zip to %LOCALAPPDATA%\Iris\app\ only when the bundle
    has changed (new version). Returns path to Iris_app.exe.
    """
    data = _get_bundle_data()
    dest_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Iris", "app")
    hash_file = os.path.join(dest_dir, ".hash")
    new_hash = hashlib.md5(data).hexdigest()

    # Skip extraction if already up to date
    if os.path.isdir(dest_dir) and os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            if f.read().strip() == new_hash:
                return os.path.join(dest_dir, "Iris_app.exe"), None

    # Show image splash screen via PowerShell
    if hasattr(sys, "_MEIPASS"):
        img_path = os.path.join(sys._MEIPASS, "splash.png")
    else:
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "splash.png")

    ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$f = New-Object System.Windows.Forms.Form
$f.FormBorderStyle = 'None'
$f.StartPosition = 'CenterScreen'
$img = [System.Drawing.Image]::FromFile('{img_path}')
$f.ClientSize = $img.Size
$f.BackgroundImage = $img
[void]$f.ShowDialog()
"""
    splash_proc = subprocess.Popen(
        ["powershell", "-NoProfile", "-Command", "-"],
        stdin=subprocess.PIPE,
        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
    )
    splash_proc.stdin.write(ps_script.encode('utf-8'))
    splash_proc.stdin.close()

    # Extract fresh copy
    if os.path.isdir(dest_dir):
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(data)) as z:
        z.extractall(dest_dir)

    with open(hash_file, "w") as f:
        f.write(new_hash)

    return os.path.join(dest_dir, "Iris_app.exe"), splash_proc

def main():
    try:
        target, splash_proc = _extract_app()
    except Exception as e:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, f"Erreur au démarrage d'Iris :\n{e}", "Iris — Erreur", 0x10)
        sys.exit(1)

    si = subprocess.STARTUPINFO()
    si.dwFlags = subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0  # SW_HIDE — no ghost window ever

    # Pass our own path so Iris_app.exe can register the correct startup entry
    own_path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
    app_proc = subprocess.Popen(
        [target, "--launcher-path", own_path] + sys.argv[1:],
        startupinfo=si,
        close_fds=True
    )

    if splash_proc is not None:
        import time
        time.sleep(1.5)
        try:
            splash_proc.kill()
        except Exception:
            pass


if __name__ == "__main__":
    main()
