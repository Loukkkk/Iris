# 👁️ EyeRest

## ✨ Features

* **🕐 Fully Configurable:** Customize your work intervals and break durations to perfectly fit your workflow.
* **🎮 Smart Suppression:** Automatically detects fullscreen games, video players, and windowed media playback to avoid interrupting you mid-session. The break queues up and fires as soon as you're done!
* **🌿 Flexible Breaks:** Features an animated full-screen overlay with choices to take your eye break immediately or pause the timer entirely.
* **⚙️ Background Mode:** Runs quietly minimized in your Windows system tray to stay out of your way.
* **🚀 Startup Friendly:** Optional Windows startup launch, including a silent background-only mode.
* **📍 True Portability:** Automatically updates the Windows startup registry entry if you move the executable to another folder.
* **🪶 Ultra Low CPU Usage:** Near-zero resource usage with practically 0% CPU consumption (max 0.1% under stress).

## 🛠️ Built With

* **Python**
* **PyQt6**
* **Pillow**
* **winrt**

## 🚀 How to Download and Run

1. Go to the **Releases** section on the right side of this repository.
2. Download the latest version (`EyeRest.exe` or its `.zip` archive).
3. Launch the `.exe` file. **No installation required!**

---

## ⚠️ Disclaimer

This application was fully coded by Claude (Anthropic AI). Since no other eye protection app on the market currently offers this level of customization, smart media suppression, and quality, this AI-generated solution fills the gap. 

> [!NOTE]
> The day a human developer creates a similar open-source application with equivalent or superior quality, this repository will be permanently deleted.

## 🔒 Security & Permissions

Since this is AI-generated code, transparency is key:

* **No Administrative Privileges:** This application explicitly runs with standard user permissions (`asInvoker`). It does not require, nor will it ever ask for, Administrator privileges to run or to manage its startup entry.
* **UAC Safety Indicator:** If the application ever prompts you with a Windows UAC (User Account Control) warning asking for admin rights, close it immediately—that means the binary has been altered or compromised.
---

## Quick Start (Python Script)

```bash
# 1. Clone or extract the repository
cd eyerest

# 2. Install the required dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

---

## Build Standalone .exe (Optional)

```Bash
pip install pyinstaller
build.bat
# The compiled executable will be located in dist/EyeRest.exe
```

---

## File Structure

```
eyerest/
├── main.py               # Application entry point
├── icon_gen.py           # Programmatic icon generator
├── requirements.txt      # Python dependencies
├── build.bat             # Automated Windows build script
├── app.manifest          # Windows execution manifest (asInvoker)
├── splash.png            # PyInstaller splash screen image
├── icon.ico              # Cached application icon
└── app/
    ├── __init__.py
    ├── settings.py       # JSON configuration persistence (%APPDATA%\EyeRest\settings.json)
    ├── detector.py       # Fullscreen/Game/Video detection via native Windows API (ctypes & winrt)
    ├── timer_engine.py   # Core timer logic running on a low-overhead 1Hz QTimer
    ├── break_overlay.py  # Animated semi-transparent full-screen break overlay
    ├── main_window.py    # Main UI featuring the animated progress ring and settings
    ├── tray.py           # System tray icon and context menu management
    └── startup.py        # Windows Registry integration for startup handling (HKCU)
```

---

## How Smart Media Suppression Works    

To avoid interrupting you mid-game or mid-movie, EyeRest detects fullscreen applications using four distinct native layers (with zero active polling overhead):

* SHQueryUserNotificationState: Detects running Direct3D applications (games), presentation modes, or "busy" full-screen states.

* Window vs. Monitor Geometry: Compares the active window rectangle bounds against the monitor resolution to detect generic borderless fullscreen applications.

* Hardcoded Process List: Automatically flags known media players like VLC, MPC-HC, PotPlayer, MPV, etc.

* Windows Media Session API (SMTC): Detects windowed media playback (like Netflix or YouTube running in a browser tab).

If a break is due while suppression is active, the alert queues up silently and fires immediately once you exit the fullscreen application or stop media playback.

---

## Configuration File Path

User preferences and settings are stored locally in standard JSON format at:
`%APPDATA%\EyeRest\settings.json`
