# 👁️ Iris

A lightweight and portable eye protection application for Windows designed to reduce eye strain. It reminds you to look away from your screen at custom intervals, following the 20-20-20 rule or your own routine.

## ✨ Features

* **🕐 Fully Configurable:** Customize your work intervals and break durations to perfectly fit your workflow.
* **🎮 Smart Suppression:** Automatically detects fullscreen games, video players, and windowed media playback to avoid interrupting you mid-session. The break queues up and fires as soon as you're done!
* **🌿 Flexible Breaks:** Features an animated full-screen overlay with choices to take your eye break immediately or pause the timer entirely.
* **⚙️ Background Mode:** Runs quietly minimized in your Windows system tray to stay out of your way.
* **🚀 Startup Friendly:** Optional Windows startup launch, including a silent background-only mode.
* **📍 True Portability:** Automatically updates the Windows startup registry entry if you move the executable to another folder.
* **🪶 Ultra Low CPU Usage:** Near-zero resource usage with practically 0% CPU consumption (max 0.1% under stress).
* **🌐 Language:** Available in English and French. It's is auto-detected from your OS on first launch.

---

## 🗑️ Uninstall

Iris does not have an installer — to fully remove it:

1. Exit Iris (right-click the tray icon → **Quit**)
2. Delete `Iris.exe`
3. Delete the following folders:
   - `%APPDATA%\Iris` (settings)
   - `%LOCALAPPDATA%\Iris` (application cache)
4. If you had **Start with Windows** enabled, remove the startup entry:
   - Open **Registry Editor** (`regedit`)
   - Navigate to `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
   - Delete the `Iris` entry

> [!TIP]
> The easiest way to remove the startup entry is to uncheck **Start with Windows** in Iris settings *before* quitting.

---

## 🛠️ Built With

* **Python**
* **PyQt6**
* **Pillow**
* **winrt**

---

## 🚀 How to Download and Run

1. Go to the **Releases** section on the right side of this repository.
2. Download the latest version (`Iris.exe`).
3. Launch the file. **No installation required!**

---

## ⚠️ Disclaimer

This application was fully coded by Claude (Anthropic AI). Since no other eye protection app on the market currently offers this level of modern quality, smart media suppression, but simplicity and lightness, this AI-generated solution fills the gap.

> [!NOTE]
> The day a human developer creates a similar open-source application with equivalent or superior quality, this repository will be permanently deleted.

---

## 🔒 Security & Permissions

Since this is AI-generated code, transparency is key:

* **No Administrative Privileges:** This application explicitly runs with standard user permissions (`asInvoker`). It does not require, nor will it ever ask for, Administrator privileges to run or to manage its startup entry.
* **UAC Safety Indicator:** If the application ever prompts you with a Windows UAC (User Account Control) warning asking for admin rights, close it immediately—that means the binary has been altered or compromised.

---

## Quick Start (Python Script)

```bash
# 1. Clone or extract the repository
cd iris

# 2. Install the required dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

---

## Build Standalone .exe (Optional)

```bash
pip install pyinstaller
build.bat
# The compiled executable will be located in dist/Iris.exe
```

---

## File Structure

```
iris/
├── main.py               # Application entry point
├── icon_gen.py           # Programmatic icon generator
├── requirements.txt      # Python dependencies
├── build.bat             # Automated Windows build script
├── app.manifest          # Windows execution manifest (asInvoker)
├── splash.png            # PyInstaller splash screen image
├── icon.ico              # Cached application icon
└── app/
    ├── __init__.py
    ├── i18n.py           # Internationalization (English & French)
    ├── settings.py       # JSON configuration persistence (%APPDATA%\Iris\settings.json)
    ├── detector.py       # Fullscreen/Game/Video detection via native Windows API (ctypes & winrt)
    ├── timer_engine.py   # Core timer logic running on a low-overhead 1Hz QTimer
    ├── break_overlay.py  # Animated semi-transparent full-screen break overlay
    ├── main_window.py    # Main UI featuring the animated progress ring and settings
    ├── tray.py           # System tray icon and context menu management
    └── startup.py        # Windows Registry integration for startup handling (HKCU)
```

---

## How Smart Media Suppression Works

To avoid interrupting you mid-game or mid-movie, Iris detects fullscreen applications using four distinct native layers (with zero active polling overhead):

* **SHQueryUserNotificationState:** Detects running Direct3D applications (games), presentation modes, or "busy" full-screen states.
* **Window vs. Monitor Geometry:** Compares the active window rectangle bounds against the monitor resolution to detect generic borderless fullscreen applications.
* **Hardcoded Process List:** Automatically flags known media players like VLC, MPC-HC, PotPlayer, MPV, etc.
* **Windows Media Session API (SMTC):** Detects windowed media playback (like Netflix or YouTube running in a browser tab).

If a break is due while suppression is active, the alert queues up silently and fires immediately once you exit the fullscreen application or stop media playback.

---

## Cache & Application Data Locations (Windows)

Soundboard Pro stores its configuration, temporary engine caches, and downloaded audio files inside the Windows user local directory.

* Main Application Directory:
```%LOCALAPPDATA%\SoundboardPro\```
(Equivalent to: C:\Users\<YourUsername>\AppData\Local\SoundboardPro\)

Inside this folder, you will find:
- config.json : Contains your primary settings, collection lists, volumes, and custom hotkey bindings.
- devices_cache.json : Stores Windows PortAudio endpoints hardware fingerprints to accelerate application boot time.
- numba_cache\ : Dedicated internal directory holding pre-compiled Numba LLVM bytecode acceleration views to eliminate runtime sound loading latency.
- downloads\ : Cache directory housing .mp3 / .wav assets downloaded on-the-fly via the built-in online Freesound and YouTube streaming loaders.
