@echo off
setlocal EnableDelayedExpansion

:: Set title
title Job Tracker Application Installer

:: Store current directory
set "CURRENT_DIR=%~dp0"
set "APP_NAME=JobTracker"
set "INSTALL_DIR=C:\Program Files\%APP_NAME%"

cls
echo ==============================================
echo          Job Tracker Application Installer
echo ==============================================
echo.

:: Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if !errorLevel! == 0 (
    echo [✓] Python is installed
) else (
    echo [!] Python is not installed
    echo.
    choice /C YN /M "Would you like to install Python now"
    if !errorLevel! == 1 (
        echo.
        echo Installing Python...
        echo Please wait while the Python installer downloads...
        powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe', 'python_installer.exe')"
        start /wait python_installer.exe /quiet PrependPath=1
        del python_installer.exe
    ) else (
        echo.
        echo Installation cancelled.
        goto :exit
    )
)

:: Check required packages
echo.
echo Checking required packages...
if exist "requirement.txt" (
    pip install -r "requirement.txt" >nul 2>&1
    if !errorLevel! == 0 (
        echo [✓] All required packages installed
    ) else (
        echo [!] Some packages could not be installed
        choice /C YN /M "Would you like to try installing packages again"
        if !errorLevel! == 1 (
            pip install -r "requirement.txt"
        )
    )
) else (
    echo [!] requirement.txt not found
)

echo.
echo ==============================================
echo                Installation Options
echo ==============================================
echo.
echo 1. Standalone Version
echo    - Run from current location
echo    - No system modifications needed
echo    - Can be moved to any folder
echo.
echo 2. System Installation
echo    - Install to Program Files
echo    - Create desktop shortcut
echo    - Proper system integration
echo.

choice /C 12 /M "Please select an option (1 or 2)"
if !errorLevel! == 1 (
    echo.
    echo [✓] Setting up standalone version...
    echo.
    echo Installation completed! You can now:
    echo - Double-click launch.bat to start the application
    echo - Move the entire folder anywhere you want
    echo.
    pause
    goto :run_app
) else (
    echo.
    echo [i] System installation selected...
    
    :: Check admin rights
    net session >nul 2>&1
    if !errorLevel! == 0 (
        goto :do_install
    ) else (
        echo [!] Administrator privileges required.
        echo     The installer will restart with admin rights...
        powershell -Command "Start-Process '%~f0' -Verb RunAs"
        exit
    )
)

:do_install
echo.
echo Installing to Program Files...
echo.

:: Create program directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Copy all files
echo [i] Copying application files...
xcopy /E /I /Y "%CURRENT_DIR%*.*" "%INSTALL_DIR%" >nul

:: Create desktop shortcut
echo [i] Creating desktop shortcut...
set "SHORTCUT_PATH=%USERPROFILE%\Desktop\%APP_NAME%.lnk"
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%SHORTCUT_PATH%'); $SC.TargetPath = '%INSTALL_DIR%\launch.bat'; $SC.WorkingDirectory = '%INSTALL_DIR%'; $SC.Save()"

echo.
echo Installation completed successfully!
echo.
echo A shortcut has been created on your desktop.
echo You can now start the application from:
echo - The desktop shortcut
echo - %INSTALL_DIR%\launch.bat
echo.
pause

:run_app
cls
echo Starting Job Tracker...
python "%CURRENT_DIR%job_tracker.py"

:exit
endlocal
exit /b