# 👁️ EyeRest

A lightweight and portable eye protection application for Windows designed to reduce eye strain. It reminds you to look away from your screen at custom intervals, following the 20-20-20 rule or your own routine.

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
