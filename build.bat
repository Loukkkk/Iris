@echo off
cd /d "%~dp0"
title Iris — Build

echo.
echo  === Iris Build ===
echo  Dossier : %CD%
echo.

python --version
if errorlevel 1 ( echo ERREUR : Python introuvable. & pause & exit /b 1 )

echo.
echo [1/4] Installation des dependances...
python -m pip install PyQt6 pillow winrt-Windows.Media.Control winrt-Windows.Foundation pyinstaller --quiet
if errorlevel 1 ( echo ERREUR pip & pause & exit /b 1 )
echo OK

echo.
echo [2/4] Pre-generation du cache icone...
python -c "from app.icon_cache import get_ico_bytes; get_ico_bytes(); print('  OK')"
if errorlevel 1 ( echo ERREUR icon cache & pause & exit /b 1 )

echo.
echo [3/4] Nettoyage...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist Iris.spec del /q Iris.spec

echo.
echo [4/4] Compilation...
python -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "Iris" ^
    --icon "icon.ico" ^
    --splash splash.png ^
    --hidden-import winreg ^
    --collect-all PyQt6 ^
    --add-data "app;app" ^
    main.py
if errorlevel 1 ( echo ERREUR PyInstaller & pause & exit /b 1 )

if exist build rmdir /s /q build
if exist Iris.spec del /q Iris.spec

echo.
echo  === Build termine ! dist\Iris.exe ===
echo.
explorer dist
pause
