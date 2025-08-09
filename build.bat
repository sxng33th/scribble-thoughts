@echo off
setlocal enabledelayedexpansion

echo ====================================
echo  Building ScribbleThoughts Executable
echo ====================================
echo.

echo [1/4] Installing dependencies...
call pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo Failed to install dependencies. Please check your internet connection.
    pause
    exit /b !errorlevel!
)

echo.
echo [2/4] Installing PyInstaller...
call pip install pyinstaller
if !errorlevel! neq 0 (
    echo Failed to install PyInstaller.
    pause
    exit /b !errorlevel!
)

echo.
echo [3/4] Building executable...
call python build.py
if !errorlevel! neq 0 (
    echo Build failed with error code !errorlevel!
    pause
    exit /b !errorlevel!
)

echo.
echo [4/4] Build complete!
echo.
echo The executable has been created in the 'dist' folder.
echo.

if exist "dist" (
    echo Opening the dist folder...
    start "" "dist"
)

pause
