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
echo [1/7] Installation des dependances...
python -m pip install PyQt6 pillow winrt-Windows.Media.Control winrt-Windows.Foundation pyinstaller --quiet
if errorlevel 1 ( echo ERREUR pip & pause & exit /b 1 )
echo OK

echo.
echo [2/7] Nettoyage...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist Iris.spec del /q Iris.spec
if exist Iris_app.spec del /q Iris_app.spec
if exist Iris_app.zip del /q Iris_app.zip

echo.
echo [3/7] Compilation de l'application principale (onedir)...
python -m PyInstaller ^
    --noconfirm ^
    --onedir ^
    --windowed ^
    --name "Iris_app" ^
    --icon "icon.ico" ^
    --hidden-import winreg ^
    --collect-all PyQt6 ^
    --add-data "app;app" ^
    --add-data "icon.ico;." ^
    --exclude-module tkinter ^
    --exclude-module unittest ^
    --exclude-module pydoc ^
    --exclude-module doctest ^
    --exclude-module difflib ^
    --exclude-module ftplib ^
    --exclude-module imaplib ^
    --exclude-module smtplib ^
    --exclude-module telnetlib ^
    --exclude-module xmlrpc ^
    --exclude-module lib2to3 ^
    --exclude-module multiprocessing ^
    --exclude-module numpy ^
    --exclude-module pandas ^
    --exclude-module matplotlib ^
    main.py
if errorlevel 1 ( echo ERREUR PyInstaller (app) & pause & exit /b 1 )

echo.
echo [4/7] Compression du dossier Iris_app en zip...
python -c "import zipfile, os; z=zipfile.ZipFile('Iris_app.zip','w',zipfile.ZIP_DEFLATED); [z.write(os.path.join(r,f), os.path.relpath(os.path.join(r,f),'dist/Iris_app')) for r,d,fs in os.walk('dist/Iris_app') for f in fs]; z.close(); print('  OK -', round(os.path.getsize('Iris_app.zip')/1024/1024,1), 'MB')"
if errorlevel 1 ( echo ERREUR zip & pause & exit /b 1 )

echo.
echo [5/7] Compilation du launcher (Iris.exe) avec Iris_app.zip integre...
python -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "Iris" ^
    --icon "icon.ico" ^
    --add-data "Iris_app.zip;." ^
    launcher.py
if errorlevel 1 ( echo ERREUR PyInstaller (launcher) & pause & exit /b 1 )

echo.
echo [6/7] Nettoyage...
if exist build rmdir /s /q build
if exist Iris.spec del /q Iris.spec
if exist Iris_app.spec del /q Iris_app.spec
if exist Iris_app.zip del /q Iris_app.zip
if exist dist\Iris_app rmdir /s /q dist\Iris_app

echo.
echo  === Build termine ! dist\Iris.exe ===
echo  Premier lancement : extraction de l'app (quelques secondes)
echo  Lancements suivants : demarrage instantane
echo.
explorer dist
pause
